from flask import Flask, request
import estnltk
from estnltk import Text

PUNCTUATION_MARKS = list('.,-!?"\'/\\[]()')
STOP_WORDS = ["ja", "et", "aga", "sest", "kuigi", "vaid", "kuna"]

def json_to_text(req, key="text"):
    return req.get_json()[key]