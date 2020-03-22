# Import analyzers
from ThesisAnalyzer.Services.Analysis import \
    overused_word_analyzer, tag_analyzer, \
    sentences_length_analyzer, impersonality_analyzer

from ThesisAnalyzer.Models.Analysis import SentencesLengthSummary, ImpersonalitySummary, TextSummmary
from ThesisAnalyzer.Models.Summary import Summary
from ThesisAnalyzer.Services.Analysis.tag_analyzer import TagSummary
from ThesisAnalyzer.Config import analysis as config
from ThesisAnalyzer.Services import profiler
from ThesisAnalyzer.Services import utils

from timeit import default_timer as timer
from estnltk import Text
from flask import jsonify
import jsonpickle
import os


def analyze(text):
    """ The main function that starts all analyses """
    start = timer()

    # Set jsonpickle settings
    jsonpickle.set_preferred_backend("json")
    jsonpickle.set_encoder_options("json", ensure_ascii=False)

    # The main summary to be returned from the API
    summary = Summary()

    # Since finding the sentences layer takes time, do it once and pass it as an argument for the analyzers
    if config.ANALYZE_OVERUSED_WORDS or config.ANALYZE_SENTENCE_LENGTH or \
            config.ANALYZE_IMPERSONALITY or config.ANALYZE_TAGS:

        text_obj = Text(text).tag_layer()
        sentences_layer = text_obj.sentences

        # Impersonality analyzer
        if config.ANALYZE_IMPERSONALITY:
            summary.impersonality_summary = impersonality_analyzer.analyze(
                text, sentences_layer)

        # Overused words analysis
        if config.ANALYZE_OVERUSED_WORDS:
            summary.text_summary = overused_word_analyzer.analyze(
                text, sentences_layer)

        # Clause analysis
        if config.ANALYZE_SENTENCE_LENGTH:
            summary.sentences_length_summary = sentences_length_analyzer.analyze(
                text, sentences_layer)

        # Tag analysis
        if config.ANALYZE_TAGS:
            summary.tag_summary = tag_analyzer.analyze(
                text, text_obj, summary.text_summary.word_count)

    end = timer()

    summary.elapsed_time = round(end - start, 3)

    return utils.encode(summary)
