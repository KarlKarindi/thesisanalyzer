import estnltk
from estnltk import Text
import utils as utils
import simplejson as json

def words(text):
    words_with_punct = Text(text).lemmas
    words = [w for w in words_with_punct if w not in utils.PUNCTUATION_MARKS]
    return words

def analyze_general(content):
    w_all = words(content)
    w_unique = set(w_all)
    print("Töös on kokku", len(w_all), "sõna.")
    print("Nendest", len(w_unique), "on unikaalsed")
    return "TODO: MAKE"

def analyze_style(content):
    t = Text(content)
    sents = t.sentence_texts
    return json.dumps(sents)