from ThesisAnalyzer.Services.Constants import constants

from flask import Flask, request, jsonify
from estnltk import Text
import jsonpickle
import estnltk

PUNCTUATION_MARKS = list('.,-!?"\'/\\[]()')

STOP_WORDS = ["ja", "et", "aga", "sest", "kuigi", "vaid", "kuna"]


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


def is_word_in_quotes(word, previous_word, in_quotes):
    """ Checks whether word is in quotes or not.
        Parameters:
            word (String) - Examples: "car; car; car"; car.
            previous_word (String) - the previous word that came prior to the word parameter
            in_quotes (boolean) - current status whether text is already in quotes or not
        Returns: (boolean) whether text is in quotes or not
    """

    # Ending the quote
    if previous_word is not None and in_quotes:
        if previous_word.endswith(constants.QUOTATION_MARK_UP):
            in_quotes = False
        # If second to last letter is an ending quotation mark
        elif len(previous_word) > 2:
            if previous_word[-2] == constants.QUOTATION_MARK_UP:
                in_quotes = False

    # Beginning the quote
    if not in_quotes and (word.startswith(constants.QUOTATION_MARK_UP) or
                          word.startswith(constants.QUOTATION_MARK_LOW)):
        in_quotes = True

    return in_quotes
