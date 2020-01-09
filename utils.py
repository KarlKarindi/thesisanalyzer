from flask import Flask, request
import estnltk
import utils as utils
from estnltk import Text

PUNCTUATION_MARKS = list('.,-!?"\'/\\')

def json_to_text(req, key="text"):
    return req.get_json()[key]