from ThesisAnalyzer.Services.Constants import constants

from flask import Flask, request, jsonify
from estnltk import Text, layer_operations
import jsonpickle
import estnltk

PUNCTUATION_MARKS = list('.,-!?"\'/\\[]()')

STOP_WORDS = ["ja", "et", "aga", "sest", "kuigi", "vaid", "kuna"]


def json_to_text(req, key="text"):
    return req.get_json()[key]


def encode(Object):
    return(jsonpickle.encode(Object, unpicklable=False))


def get_sentences_layer(text):
    """ Finds all the sentences in a text.
        Parameters:
            text (string) - clean text to find sentences from.
        Returns:
            sentences (list) - list of sentences as Text objects
    """
    text = Text(text)
    text.tag_layer()
    return text.sentences
