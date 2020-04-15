# Analyzers
from ThesisAnalyzer.Services.Analysis import overused_word_analyzer, tag_analyzer, \
    sentences_analyzer, impersonality_analyzer, \
    officialese_analyzer

# Database models
from ThesisAnalyzer.Models.Database import Formrequest, LongSentence, TextStatistics, \
    PersonalSentence, OverusedWord, ClusterOverusedWord

from ThesisAnalyzer.Models.Analysis import SentencesSummary, ImpersonalitySummary, TextSummmary
from ThesisAnalyzer.Models.Summary import Summary
from ThesisAnalyzer.Services.Analysis.tag_analyzer import TagSummary
from ThesisAnalyzer.Config import analysis as config
from ThesisAnalyzer.Services import profiler, utils
from ThesisAnalyzer import db

from timeit import default_timer as timer
from estnltk import Text
from flask import jsonify
import jsonpickle
import datetime
import os


def analyze(text, user_form=False):
    """ The main function that starts all analyses.
        Parameters:
            text (string) - the original string text that will be analysed.
            user_form (boolean) - whether this function was called out from the user form or not.
        Returns:
            summary (Summary) - a Summary object that contains all the analysis data.
    """
    start = timer()

    # If the request was made in the user form and and LOG_TO_DATABASE is true, log the request
    log_to_database = user_form and config.LOG_TO_DATABASE

    # Set jsonpickle settings
    jsonpickle.set_preferred_backend("json")
    jsonpickle.set_encoder_options("json", ensure_ascii=False)

    # The main summary to be returned from the API
    summary = Summary()

    if log_to_database:
        # Add the user submitted text to the database
        submission = Formrequest(datetime.datetime.now())
        db.session.add(submission)
        db.session.commit()
        summary.id = submission.id

    # Since finding the sentences layer takes time, do it once and pass it as an argument for the analyzers
    sentences_layer_is_necessary = utils.is_sentences_layer_necessary(config)

    if sentences_layer_is_necessary:
        text_obj = Text(text).tag_layer()
        sentences_layer = text_obj.sentences

        # Impersonality analyzer
        if config.ANALYZE_IMPERSONALITY:
            summary.impersonality_summary = impersonality_analyzer.analyze(text, sentences_layer)
            if log_to_database:
                impers = summary.impersonality_summary
                for sentence in impers.sentences_with_pv.keys():
                    db.session.add(PersonalSentence(summary.id, sentence))

        # Overused words analysis
        if config.ANALYZE_OVERUSED_WORDS:
            summary.text_summary = overused_word_analyzer.analyze(
                text, sentences_layer)
            if log_to_database:
                ows_list = summary.text_summary.overused_word_summary
                for ows in ows_list:
                    insert_data = OverusedWord(
                        summary.id, ows.lemma, ows.times_used)
                    db.session.add(insert_data)
                    db.session.commit()  # Commit must be made or we aren't able to get the id of ows
                    for cluster in ows.clusters:
                        db.session.add(ClusterOverusedWord(
                            insert_data.id, cluster.text, cluster.sentence_position[0], cluster.sentence_position[1]))

        # Clause analysis
        if config.ANALYZE_SENTENCE_LENGTH:
            summary.sentences_summary = sentences_analyzer.analyze(text, sentences_layer)
            if log_to_database:
                for sentence in summary.sentences_summary.long_sentences:
                    db.session.add(LongSentence(summary.id, sentence))

        # Tag analysis
        if config.ANALYZE_TAGS and summary.text_summary is not None:
            summary.tag_summary = tag_analyzer.analyze(text, text_obj, summary.text_summary.word_count)
            if log_to_database:
                db.session.add(TextStatistics(summary.id,
                                              summary.text_summary.sentence_count,
                                              summary.text_summary.word_count,
                                              summary.tag_summary.adverb_count,
                                              summary.tag_summary.pronoun_count))

        # Officialese analysis
        if config.ANALYZE_OFFICIALESE:
            summary.officialese_summary = officialese_analyzer.analyze(text, text_obj, sentences_layer)

    end = timer()

    summary.elapsed_time = round(end - start, 3)

    if log_to_database:
        Formrequest.query.get(summary.id).successful = True
        db.session.commit()
        print("Logged request to database.")

    return utils.encode(summary)


def add_html_to_database(id, html):
    Formrequest.query.get(id).result = html
    db.session.commit()
