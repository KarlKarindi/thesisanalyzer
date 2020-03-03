from ThesisAnalyzer.Services import utils
from ThesisAnalyzer.Services.utils import QuoteAnalyzer
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
    sentences = utils.find_sentences(text)

    # Then analyze singular sentences
    for sentence in sentences:
        personal_verbs = find_pv_in_sentence(sentence)

        # If the sentence contains personal verbs, add the verbs to dict
        if len(personal_verbs) > 0:
            sentences_with_pv[sentence.text] = personal_verbs

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

    quote_analyzer = QuoteAnalyzer()

    for analysis in analyzed_sentence:
        word = analysis.text

        # Check if word is in quotes or not
        # FIXME: Kaldkirjas tekst ka sama, mis tsitaadis
        # FIXME: Võõrkeelsed asjad esile tõstetud kaldkirjaga
        in_quotes = quote_analyzer.is_word_in_quotes(word)

        if not in_quotes:
            # Since there may be multiple roots/endings, we check through all of them.
            if ((constants.VERB in analysis.partofspeech) and
                    "sin" in analysis.ending or
                    "in" in analysis.ending or
                    "n" in analysis.ending or
                    "mina" in analysis.root):

                if word not in personal_verbs:
                    personal_verbs.append(word)

    return personal_verbs
