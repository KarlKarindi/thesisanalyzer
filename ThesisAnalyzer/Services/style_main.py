from ThesisAnalyzer.Services.Analysis.Style import overused_word_analyzer, clause_analyzer, tag_analyzer
from ThesisAnalyzer.Services.Analysis.Style.overused_word_analyzer import TextSummmary, OverusedWordSummary
from ThesisAnalyzer.Services.Analysis.Style.tag_analyzer import AdverbSummary
from ThesisAnalyzer.Models.Feedback import StyleFeedback
from ThesisAnalyzer.Models.StyleSummary import StyleSummary
from ThesisAnalyzer.Services import utils

from flask import jsonify
import jsonpickle


def analyze(request):
    """ The main function that starts all analyses related to style in the text """
    text = utils.json_to_text(request)

    # Set jsonpickle settings
    jsonpickle.set_preferred_backend("json")
    jsonpickle.set_encoder_options("json", ensure_ascii=False)

    styleSummary = StyleSummary()

    # Word repeat analysis
    # textSummary = overused_word_analyzer.analyze(text)

    # Clause analysis
    clause_analyzer.analyze(text)

    # Tag analysis
    # adverbSummary = tag_analyzer.analyze(text)

    # Set attributes for styleSummary
    #styleSummary.adverbSummary = adverbSummary
    #styleSummary.textSummary = textSummary

    return encode(styleSummary)


def encode(Object):
    return(jsonpickle.encode(Object, unpicklable=False))
