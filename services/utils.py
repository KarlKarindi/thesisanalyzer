from flask import Flask, request
import estnltk
from estnltk import Text

PUNCTUATION_MARKS = list('.,-!?"\'/\\[]()')


STOP_WORDS = ["ja", "et", "aga", "sest", "kuigi", "vaid", "kuna"]


def get_most_frequent_lemmas():
    data = {}
    lines = 0
    with open("C:\\Users\\Karl\\PythonProjects\\ThesisAnalyzer\\lemma_kahanevas.txt", "r", encoding="utf-8") as file:
        for line in file:
            if lines > 500:
                break
            print(line)
            lines += 1

    return True


def json_to_text(req, key="text"):
    return req.get_json()[key]
