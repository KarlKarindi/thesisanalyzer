from ThesisAnalyzer.Constants import constants

from flask import Flask, request, jsonify
from estnltk import Text, layer_operations
import jsonpickle
import estnltk
import nltk

PUNCTUATION_MARKS = list('.,-!?"\'/\\[]()')

STOP_WORDS = ["ja", "et", "aga", "sest", "kuigi", "vaid", "kuna"]


def json_to_text(req, key="text"):
    return req.get_json()[key]


def encode(Object):
    return(jsonpickle.encode(Object, unpicklable=False))


def get_sentences_layer(text):
    """ Finds all the sentences in a text.
        Parameters:
            text (string) - clean text to find sentences from.
        Returns:
            sentences (list) - list of sentences as Text objects
    """
    text = Text(text)
    text.tag_layer()
    return text


def words_without_punctuation(text):
    words_with_punct = Text(text).word_texts
    words_without_punctuation = [w for w in words_with_punct if w.isalpha()]
    return words_without_punctuation


def lemmas_without_punctuation(text):
    lemmas_with_punct = Text(text).lemmas
    lemmas_without_punctuation = [w for w in lemmas_with_punct if w.isalpha()]
    return lemmas_without_punctuation


def tag_text(text):
    laused = nltk.sent_tokenize(text)
    return [list(zip(Text(text).word_texts, Text(lause).postags)) for lause in laused]


def most_frequent_words(words, until=30):
    """ Creates a frequency distribution by lemmas """
    return nltk.FreqDist(words).most_common()[:until]


def is_sentences_layer_necessary(config):
    return config.ANALYZE_OVERUSED_WORDS or config.ANALYZE_SENTENCE_LENGTH or \
        config.ANALYZE_IMPERSONALITY or config.ANALYZE_TAGS
