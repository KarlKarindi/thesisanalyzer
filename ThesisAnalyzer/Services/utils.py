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


# FIXME: Last word in a quote is incorrectly marked not in quotes.
def is_word_in_quotes(word, in_quotes):
    """ Checks whether word is in quotes.
        Parameters:
            word (String) - Examples: "car; car; car"; car.
            in_quotes (boolean) - current status whether text is already in quotes or not
        Returns: (boolean) whether text is in quotes or not
    """
    if in_quotes and word.endswith('"'):
        in_quotes = False
    if not in_quotes and (word.startswith('"') or word.startswith('„')):
        in_quotes = True
    return in_quotes
