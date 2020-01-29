import estnltk
from estnltk import Text
from ThesisAnalyzer.Services.utils import *
import simplejson as json
import nltk
from ThesisAnalyzer import vabamorf


def analyze_general(content):
    """ Analyzes the content and returns general statistics about the text """
    text = json_to_text(content)

    w_all = words_without_punctuation(text)
    l_all = lemmas_without_punctuation(text)
    l_unique = set(l_all)

    # print(w_all)
    #print("Töös on kokku", len(w_all), "sõna.")
    #print("Nendest", len(w_unique), "on unikaalsed")
    #print("Leksiline tihedus on", "%")
    verb_count = 0
    for i in range(len(w_all)):
        w = vabamorf.analyze(w_all[i])
        #print("("+  w[0]["text"]+", ", w[0]["analysis"][0]["partofspeech"]+")")
        if w[0]["analysis"][0]["partofspeech"] == "V":
            verb_count += 1
            print(w_all[i], w[0]["text"], w[0]["analysis"][0]["partofspeech"])

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
