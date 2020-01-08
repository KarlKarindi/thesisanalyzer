import estnltk
from estnltk import Text
import utils as utils


def analyze_general(text):
    print(utils.word_count(text))
    return "TODO: MAKE"

def analyze_style(text):
    print(Text(text).lemmas)
    return "TODO: Implement"