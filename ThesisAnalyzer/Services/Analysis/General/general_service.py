import estnltk
from estnltk import Text
from ThesisAnalyzer.Services.utils import json_to_text
import simplejson as json
import nltk
from ThesisAnalyzer import vabamorf
from ThesisAnalyzer.Services.Constants import constants
from pprint import pprint


def analyze(content):
    """ Analyzes the content and returns general statistics about the text """
    text = json_to_text(content)

    # Impersonal verb check (umbisikulise tegumoe kontroll)
    is_text_impersonal(text)

    if False is True:
        w_all = words_without_punctuation(text)
        l_all = lemmas_without_punctuation(text)
        l_unique = set(l_all)

        # print(w_all)
        # print("Töös on kokku", len(w_all), "sõna.")
        # print("Nendest", len(w_unique), "on unikaalsed")
        # print("Leksiline tihedus on", "%")
        verb_count = 0
        for i in range(len(w_all)):
            w = vabamorf.analyze(w_all[i])
            # print("("+  w[0]["text"]+", ", w[0]["analysis"][0]["partofspeech"]+")")
            if w[0]["analysis"][0]["partofspeech"] == "V":
                verb_count += 1
                print(w_all[i], w[0]["text"], w[0]
                      ["analysis"][0]["partofspeech"])
        print(w_all)

        # print(most_frequent_words(w_all))
        tag_text(text)

        # print(tag_words(text))
        tagged_sents = tag_text(text)
        i = 0

        print("VERB COUNT", verb_count)
    return "TODO: MAKE"


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


def is_text_impersonal(text):
    """ Checks if text is fully impersonal. A text is personal if it contains personal verbs (pv).
        Returns: a dictionary of sentences with words that are personal.
    """

    def find_pv_in_sentence(sentence):
        """ Parameters: sentence - String, text of the sentence being analyzed.
            Returns: list of personal verbs in the sentence.
        """
        personal_verbs = []
        analyzed_sentence = vabamorf.analyze(sentence)

        # TODO: Check whether sentence contains a quote. If personal verb is in a quote, don't add it to pv list.

        for word in analyzed_sentence:
            # Since a word may have multiple analyses, we must use a loop to iterate over them
            # In case of many options, if one of them is personal, add them to the list.
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
