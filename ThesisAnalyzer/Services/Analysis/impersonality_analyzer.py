from ThesisAnalyzer.Services import utils
from ThesisAnalyzer.Services.Analysis.TextAnalyzers.analyzers import QuoteAnalyzer
from ThesisAnalyzer.Services.Constants import constants
from ThesisAnalyzer.Models.Analysis import ImpersonalitySummary
from pprint import pprint

import estnltk
from estnltk import Text, layer_operations


def analyze(text, sentences_layer):
    """ Checks if text is fully impersonal. A text is personal if it contains personal verbs (pv).
        Returns: a dictionary of sentences with words that are personal.
    """

    quote_analyzer = QuoteAnalyzer()

    # Dictionary to store sentences and the personal verbs (pv) they have
    sentences_with_pv = {}

    # Then analyze singular sentences
    for sentence in sentences_layer:
        personal_verbs = find_pv_in_sentence(sentence, quote_analyzer)

        # If the sentence contains personal verbs, add the verbs to dict
        if len(personal_verbs) > 0:
            sentences_with_pv[sentence.enclosing_text] = personal_verbs

    text_is_impersonal = len(sentences_with_pv) == 0

    impersonalitySummary = ImpersonalitySummary(
        text_is_impersonal, sentences_with_pv)

    return impersonalitySummary


def find_pv_in_sentence(sentence, quote_analyzer):
    """ Parameters:
            sentence (String) - text of the sentence being analyzed.
            quote_analyzer (QuoteAnalyzer) - QuoteAnalyzer instance.
        Returns: list of personal verbs in the sentence.
    """
    personal_verbs = []
    analyzed_sentence = sentence.morph_analysis

    for analysis in analyzed_sentence:
        word = analysis.text

        # Check if word is in quotes or not
        # FIXME: Kaldkirjas tekst ka sama, mis tsitaadis
        # FIXME: Võõrkeelsed asjad esile tõstetud kaldkirjaga
        in_quotes = quote_analyzer.is_word_in_quotes(word)

        if not in_quotes:
            # Since there may be multiple roots/endings, we check through all of them.
            if (((constants.VERB in analysis.partofspeech) and
                    "sin" in analysis.ending or
                    "in" in analysis.ending or
                    "n" in analysis.ending or
                    "sime" in analysis.ending or
                    "ime" in analysis.ending or
                    "me" in analysis.ending) or
                    "mina" in analysis.root):
                if word not in personal_verbs:
                    personal_verbs.append(word)

    return personal_verbs
