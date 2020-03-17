#from ThesisAnalyzer import vabamorf
from ThesisAnalyzer.Services import utils
from ThesisAnalyzer.Services.Analysis.General.impersonality_analyzer import ImpersonalitySummary
from ThesisAnalyzer.Services.Analysis.General import impersonality_analyzer
from estnltk import Text

import nltk


def analyze(text):
    """ Analyzes the content and returns general statistics about the text """

    # FIXME: Bandaid solution for issue #14
    text = text.replace("–", "-")

    # Impersonal verb check (umbisikulise tegumoe kontroll)
    impersonalitySummary = impersonality_analyzer.analyze(text)

    return utils.encode(impersonalitySummary)


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
