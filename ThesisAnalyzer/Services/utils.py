from ThesisAnalyzer.Services.Constants import constants

from flask import Flask, request, jsonify
from estnltk import Text, layer_operations
import jsonpickle
import estnltk

PUNCTUATION_MARKS = list('.,-!?"\'/\\[]()')

STOP_WORDS = ["ja", "et", "aga", "sest", "kuigi", "vaid", "kuna"]


class QuoteAnalyzer(object):

    

    def __init__(self):
        self.in_quotes = False
        self.previous_word = None
        
    


def get_most_frequent_lemmas(limit=1000):
    """ Returns a dict of lemmas with counts of their usage """

    freq_dict = {}
    lines = 0

    with open("C:\\Users\\Karl\\PythonProjects\\ThesisAnalyzer\\lemma_kahanevas.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines[:limit]:
            line = line.split()
            count, lemma = line[0], line[1]
            freq_dict[lemma] = count

    return freq_dict


def json_to_text(req, key="text"):
    return req.get_json()[key]


def encode(Object):
    return(jsonpickle.encode(Object, unpicklable=False))


def is_word_in_quotes(in_quotes, word, previous_word):
    """ Checks whether word is in quotes or not.
        Parameters:
            word (String) - Examples: "," ; "hi", "'"
            previous_word (String) - the previous word that came prior to the word parameter
            in_quotes (boolean) - current status whether text is already in quotes or not
        Returns:
            in_quotes (boolean) - whether text is in quotes or not
            quotes_just_started (boolean) - whether quotes just started or not
    """
    # Assume that this word won't be skipped
    quotes_just_started = False

    # Ending the quote
    if previous_word is not None and in_quotes:
        if (previous_word == constants.QUOTATION_MARK_UP_1 or
                previous_word == constants.QUOTATION_MARK_UP_2):
            in_quotes = False

    # Starting the quote
    if not in_quotes and (word == constants.QUOTATION_MARK_UP_1 or
                          word == constants.QUOTATION_MARK_UP_2 or
                          word == constants.QUOTATION_MARK_LOW):
        # Skip setting this word to previous_word
        in_quotes, quotes_just_started = True, True

    return in_quotes, quotes_just_started


def find_sentences(text):
    """ Finds all the sentences in a text. Analyses everything.
        Parameters:
            text (string) - clean text to find sentences from.
        Returns:
            sentences (list) - list of sentences
    """

    text = Text(text)
    text.analyse("all")
    return layer_operations.split_by_sentences(
        text=text, layers_to_keep=list(text.layers), trim_overlapping=True)
