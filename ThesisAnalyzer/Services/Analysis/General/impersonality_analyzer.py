# from ThesisAnalyzer import vabamorf
from ThesisAnalyzer.Services import utils
from ThesisAnalyzer.Services.Constants import constants
from pprint import pprint

import estnltk
from estnltk import Text, layer_operations


class ImpersonalitySummary():

    def __init__(self, is_impersonal, sentences_with_pv):
        self.is_impersonal = is_impersonal
        self.sentences_with_pv = sentences_with_pv


def analyze(text):
    """ Checks if text is fully impersonal. A text is personal if it contains personal verbs (pv).
        Returns: a dictionary of sentences with words that are personal.
    """

    # Dictionary to store sentences and the personal verbs (pv) they have
    sentences_with_pv = {}
    text = Text(text)
    text.analyse("all")
    sentences = layer_operations.split_by_sentences(
        text=text, layers_to_keep=list(text.layers), trim_overlapping=True)

    # Then analyze singular sentences
    for sentence in sentences:
        pv_in_sentence = find_pv_in_sentence(sentence)

    # If sentence contains personal verbs, add the verbs to dict
    # if len(pv_in_sentence) > 0:
    #    sentences_with_pv[sentence] = pv_in_sentence

    text_is_impersonal = len(sentences_with_pv) == 0

    impersonalitySummary = ImpersonalitySummary(
        text_is_impersonal, sentences_with_pv)
    return impersonalitySummary


def find_pv_in_sentence(sentence):
    """ Parameters: sentence (String) - text of the sentence being analyzed.
        Returns: list of personal verbs in the sentence.
    """
    personal_verbs = []

    analyzed_sentence = sentence.morph_analysis

    in_quotes = False
    previous_word = None

    for analysis in analyzed_sentence:
        word = analysis.text

        # Check if word is in quotes or not
        in_quotes, quotes_just_started = is_word_in_quotes(
            in_quotes, word, previous_word)
        if not quotes_just_started:
            previous_word = word

    return personal_verbs


def is_word_in_quotes(in_quotes, word, previous_word):
    """ Checks whether word is in quotes or not.
        Parameters:
            word (String) - Examples: "," ; "hi", "'"
            previous_word (String) - the previous word that came prior to the word parameter
            in_quotes (boolean) - current status whether text is already in quotes or not
        Returns: 
            in_quotes (boolean) - whether text is in quotes or not
            quotes_just_started (boolean) - whether quotes just started or not
    """
    # Assume that this word won't be skipped
    quotes_just_started = False

    # Ending the quote
    if previous_word is not None and in_quotes:
        if (previous_word == constants.QUOTATION_MARK_UP_1 or
                previous_word == constants.QUOTATION_MARK_UP_2):
            in_quotes = False

    # Starting the quote
    if not in_quotes and (word == constants.QUOTATION_MARK_UP_1 or
                          word == constants.QUOTATION_MARK_UP_2 or
                          word == constants.QUOTATION_MARK_LOW):
        # Skip setting this word to previous_word
        in_quotes, quotes_just_started = True, True

    return in_quotes, quotes_just_started
