from ThesisAnalyzer.Services.Analysis.Style import overused_word_analyzer, tag_analyzer, sentences_length_analyzer
from ThesisAnalyzer.Services.Analysis.Style.overused_word_analyzer import TextSummmary, OverusedWordSummary
from ThesisAnalyzer.Services.Analysis.Style.Config import config
from ThesisAnalyzer.Services.Analysis.Style.tag_analyzer import TagSummary
from ThesisAnalyzer.Models.Feedback import StyleFeedback
from ThesisAnalyzer.Models.StyleSummary import StyleSummary
from ThesisAnalyzer.Services import utils
from ThesisAnalyzer.Services import profiler

from flask import jsonify
import jsonpickle


@profiler.profile
def analyze(request):
    """ The main function that starts all analyses related to style in the text """
    text = utils.json_to_text(request)

    # FIXME: Bandaid solution for issue #14
    text = text.replace("–", "-")

    # Set jsonpickle settings
    jsonpickle.set_preferred_backend("json")
    jsonpickle.set_encoder_options("json", ensure_ascii=False)

    styleSummary = StyleSummary()

    # Since finding the sentences layer takes time, do it once and pass it as an argument for the analyzers
    if config.ANALYZE_OVERUSED_WORDS or config.ANALYZE_SENTENCE_LENGTH:
        sentences_layer = utils.get_sentences_layer(text)

        # Overused words analysis
        if config.ANALYZE_OVERUSED_WORDS:
            textSummary = overused_word_analyzer.analyze(text, sentences_layer)
            styleSummary.text_summary = textSummary

        # Clause analysis
        if config.ANALYZE_SENTENCE_LENGTH:
            sentencesLengthSummary = sentences_length_analyzer.analyze(
                text, sentences_layer)
            styleSummary.sentences_length_summary = sentencesLengthSummary

    # Tag analysis
    if config.ANALYZE_TAGS:
        tagSummary = tag_analyzer.analyze(text)
        styleSummary.tag_summary = tagSummary

    return utils.encode(styleSummary)
