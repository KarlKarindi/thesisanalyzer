# Import analyzers
from ThesisAnalyzer.Services.Analysis import \
    overused_word_analyzer, tag_analyzer, \
    sentences_length_analyzer, impersonality_analyzer

from ThesisAnalyzer.Config import style as config
from ThesisAnalyzer.Services.Analysis.tag_analyzer import TagSummary
from ThesisAnalyzer.Models.Summary import Summary
from ThesisAnalyzer.Services import utils
from ThesisAnalyzer.Services import profiler

from flask import jsonify
import jsonpickle


def analyze(text):
    """ The main function that starts all analyses related to style in the text """

    # Set jsonpickle settings
    jsonpickle.set_preferred_backend("json")
    jsonpickle.set_encoder_options("json", ensure_ascii=False)

    summary = Summary()

    # Since finding the sentences layer takes time, do it once and pass it as an argument for the analyzers
    if config.ANALYZE_OVERUSED_WORDS or config.ANALYZE_SENTENCE_LENGTH or config.ANALYZE_IMPERSONALITY:
        sentences_layer = utils.get_sentences_layer(text)

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
        tagSummary = tag_analyzer.analyze(text)
        summary.tag_summary = tagSummary

    return utils.encode(summary)
