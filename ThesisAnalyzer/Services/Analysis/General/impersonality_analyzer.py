from ThesisAnalyzer import vabamorf
from ThesisAnalyzer.Services import utils
from ThesisAnalyzer.Services.Constants import constants
from pprint import pprint

import estnltk


def analyze(text):
    """ Checks if text is fully impersonal. A text is personal if it contains personal verbs (pv).
        Returns: a dictionary of sentences with words that are personal.
    """

    def find_pv_in_sentence(sentence):
        """ Parameters: sentence - String, text of the sentence being analyzed.
            Returns: list of personal verbs in the sentence.
        """
        personal_verbs = []
        analyzed_sentence = vabamorf.analyze(sentence)

        in_quotes = False

        for word in analyzed_sentence:
            # Quickly check if word is in quotes or not.
            # If the word is in quotes, it is not considered a personal verb.
            word_text = word["text"]

            # FIXME: Kaldkirjas tekst ka sama, mis tsitaadis
            # FIXME: Võõrkeelsed asjad esile tõstetud kaldkirjaga
            in_quotes = utils.is_word_in_quotes(word_text, in_quotes)

            # Since a word may have multiple analyses, we must use a loop to iterate over them
            # In case of many options, if one of them is personal, add them to the list.
            if not in_quotes:
                for w_analysis in word["analysis"]:
                    if (w_analysis["partofspeech"] == constants.VERB and
                            w_analysis["form"] == "n" or
                            w_analysis["ending"] == "in" or
                            w_analysis["ending"] == "sin" or
                            w_analysis["root"] == "mina"):

                        word_text = word["text"]
                        if word_text not in personal_verbs:
                            personal_verbs.append(word_text)

        return personal_verbs

    # Dictionary to store sentences and the personal verbs (pv) they have
    sentences_with_pv = {}

    # First divide given text into sentences
    sentences = estnltk.Text(text).sentence_texts

    # Then analyze singular sentences
    for sentence in sentences:
        pv_in_sentence = find_pv_in_sentence(
            sentence)

        # If sentence contains personal verbs, add the verbs to dict
        if len(pv_in_sentence) > 0:
            sentences_with_pv[sentence] = pv_in_sentence

    text_is_impersonal = len(sentences_with_pv) == 0
    print("TEXT_IS_IMPERSONAL", text_is_impersonal)
    pprint(sentences_with_pv)
    return text_is_impersonal
