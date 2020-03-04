from ThesisAnalyzer.Services.Constants import constants

from flask import Flask, request, jsonify
from estnltk import Text, layer_operations
import jsonpickle
import estnltk

PUNCTUATION_MARKS = list('.,-!?"\'/\\[]()')

STOP_WORDS = ["ja", "et", "aga", "sest", "kuigi", "vaid", "kuna"]


class QuoteAnalyzer(object):
    """ QuoteAnalyzer checks whether a certain word in a sentence is in quotes or not.
        Usage:
            1. Initialize a new instance of QuoteAnalyzer
            2. Take one sentence for inspection.
            3. Iterate over all of the words.
            4. For every word, call out the is_word_in_quotes(word) function with
            the word's text (string) as its argument.
    """

    def __init__(self):
        self.in_quotes = False
        self.previous_word = None

    def is_word_in_quotes(self, word):
        """ Checks whether word is in quotes or not.
            Uses self.previous_word and self.in_quotes to make a decision whether word is in quotes or not.
            Parameters:
                word (String) - Examples: "," ; "hi", "'"
            Returns:
                in_quotes (boolean) - whether the word is in quotes or not
        """
        # Assume that this word won't be skipped
        quotes_just_started = False

        # Ending the quote
        if self.previous_word is not None and self.in_quotes:
            if (self.previous_word == constants.QUOTATION_MARK_UP_1 or
                    self.previous_word == constants.QUOTATION_MARK_UP_2 or
                    self.previous_word == constants.QUOTATION_MARK_UP_3):
                self.in_quotes = False

        # Starting the quote
        if not self.in_quotes and (word == constants.QUOTATION_MARK_UP_1 or
                                   word == constants.QUOTATION_MARK_UP_2 or
                                   word == constants.QUOTATION_MARK_LOW):
            # Set quotes_just_started_to_true
            self.in_quotes, quotes_just_started = True, True

        # If quotes just started, skip setting the previous word as current word so that on the next word,
        # the same quotes won't be marked as ending the quote
        if not quotes_just_started:
            self.previous_word = word

        return self.in_quotes


def json_to_text(req, key="text"):
    return req.get_json()[key]


def encode(Object):
    return(jsonpickle.encode(Object, unpicklable=False))


def find_sentences(text):
    """ Finds all the sentences in a text. Analyses everything.
        Parameters:
            text (string) - clean text to find sentences from.
        Returns:
            sentences (list) - list of sentences
    """

    text = Text(text)
    text.analyse("all")
    return layer_operations.split_by_sentences(
        text=text, layers_to_keep=list(text.layers), trim_overlapping=True)
