import estnltk
import nltk
import statistics
import simplejson as json

# ThesisaAnalyzer imports
from ThesisAnalyzer.Services.Analysis.Style import overused_word_analyzer
from ThesisAnalyzer.Services.Analysis.Style import clause_analyzer
from ThesisAnalyzer.Services.Analysis.Style import tag_analyzer
from ThesisAnalyzer import vabamorf
from ThesisAnalyzer.Models.Feedback import StyleFeedback
from ThesisAnalyzer.Models.Lemma import Lemma
from ThesisAnalyzer import db
from ThesisAnalyzer.Services.utils import json_to_text

from flask import jsonify
from estnltk import Text, EstWordTokenizer, ClauseSegmenter
from pprint import pprint
from collections import defaultdict


def analyze(request):
    feedback = StyleFeedback()
    text = json_to_text(request)

    # Word repeat analysis
    overused_word_analyzer.analyze_overused_words(text)

    # Clause analysis
    clause_analyzer.analyze_clauses(text)

    # Tag analysis
    tag_analyzer.analyze_adverbs(text)

    return jsonify(length=feedback.length)
