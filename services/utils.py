from flask import Flask, request
import estnltk
from estnltk import Text

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
