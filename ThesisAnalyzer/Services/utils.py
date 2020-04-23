from ThesisAnalyzer.Constants import constants
from ThesisAnalyzer.Config import analysis as config

from flask import Flask, request, jsonify
from estnltk import Text, layer_operations
import jsonpickle
import estnltk
import nltk

def json_to_text(req, key="text"):
    return req.get_json()[key]


def encode(Object):
    return(jsonpickle.encode(Object, unpicklable=False))


def is_text_too_long(length):
    """ Checks if the text is too long for analysis in the user form. """
    if length > config.ANALYSIS_MAX_CHAR_COUNT:
        return True
    return False


def is_sentences_layer_necessary(config):
    return config.ANALYZE_OVERUSED_WORDS or \
        config.ANALYZE_SENTENCES or \
        config.ANALYZE_IMPERSONALITY or \
        config.ANALYZE_TAGS or \
        config.ANALYZE_OFFICIALESE
