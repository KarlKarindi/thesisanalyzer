import estnltk
from estnltk import Text
from .utils import *
import simplejson as json


def words(text):
    words_with_punct = Text(text).lemmas
    words = [w for w in words_with_punct if w not in PUNCTUATION_MARKS]
    return words

def analyze_general(content):
    text = json_to_text(content)
    w_all = words(text)
    w_unique = set(w_all)
    print("Töös on kokku", len(w_all), "sõna.")
    print("Nendest", len(w_unique), "on unikaalsed")
    print("Leksiline tihedus on seega", (round(len(w_unique) / len(w_all) * 100)) , "%")
    
    return "TODO: MAKE"

def analyze_style(content):
    t = Text(content)
    sents = t.sentence_texts
    return json.dumps(sents)