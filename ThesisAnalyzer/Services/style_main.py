from ThesisAnalyzer.Services.Analysis.Style import overused_word_analyzer, clause_analyzer, tag_analyzer
from ThesisAnalyzer.Services.Analysis.Style.overused_word_analyzer import TextSummmary, OverusedWordSummary
from ThesisAnalyzer.Models.Feedback import StyleFeedback
from ThesisAnalyzer.Services import utils

from flask import jsonify
import jsonpickle


def analyze(request):
    feedback = StyleFeedback()
    text = utils.json_to_text(request)

    jsonpickle.set_preferred_backend("json")
    jsonpickle.set_encoder_options("json", ensure_ascii=False)

    # Word repeat analysis
    textSummary = overused_word_analyzer.analyze(text)
    
    # Clause analysis
    # clause_analyzer.analyze(text)

    # Tag analysis
    # tag_analyzer.analyze(text)

    return encode(textSummary)

def encode(Object):
    return(jsonpickle.encode(Object, unpicklable=False))