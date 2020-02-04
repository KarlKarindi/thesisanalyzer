from ThesisAnalyzer.Services.Analysis.Style import overused_word_analyzer, clause_analyzer, tag_analyzer
from ThesisAnalyzer.Models.Feedback import StyleFeedback
from ThesisAnalyzer.Services.utils import json_to_text

from flask import jsonify


def analyze(request):
    feedback = StyleFeedback()
    text = json_to_text(request)

    # Word repeat analysis
    #overused_word_analyzer.analyze_overused_words(text)

    # Clause analysis
    clause_analyzer.analyze_clauses(text)

    # Tag analysis
    # tag_analyzer.analyze_adverbs(text)

    return jsonify(length=feedback.length)
