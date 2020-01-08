from flask import Flask, request
import estnltk
from estnltk import Text

def json_to_text(req, key="text"):
    return req.get_json()[key]

def word_count(text):
    return Text(text).word_texts