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


def preprocess_text(original_text, sentences_layer):
    """ Preprocesses the text, calls out the functions
        find_sentences_with_index_and_span() and get_words_in_sentence()
        Parameters:
            original_text (string) - A string of the original text
            sentences_layer (Layer) - The Text.sentences layer
        Returns:
            sentences (dict) - output of find_sentences_with_index_and_span()
            words (dict) - output of get_words_in_sentence()
            sentence_index (int) - count of sentences
    """

    sentences = find_sentences_with_index_and_span(
        original_text, sentences_layer)
    words = []

    sentence_index = 0  # Necessary in case there are no sentences
    for sentence_index, (span, sentence) in enumerate(sentences.items()):
        words.extend(get_words_in_sentence(span, sentence, sentence_index))
        sentence_index += 1

    return sentences, words


def find_sentences_with_index_and_span(text, sentences_layer):
    """ Returns: dictionary with tuplet of (start, end) as key and
        dictionary of sentence with index, text, start and end values
    """

    keys, values = [], []

    sentence_spans = sentences_layer[["start", "end"]]

    for i, sentence in enumerate(sentences_layer):
        start = sentence_spans[i][0]
        end = sentence_spans[i][1]
        values.append(
            ({"index": i, "text": sentence.enclosing_text, "start": start, "end": end}))
        keys.append((start, end))

    return dict(zip(keys, values))


def get_words_in_sentence(sentence_span, sentence, sentence_index):
    """ Returns a list of all words in a sentence.
        Words in this case are dictionaries that have attributes:
            text (string) - text string of the word
            pos (string) - part of speech of the word
            lemma (string) - lemma of the word
            start (int) - start index of the word in the whole text
            end (int) - end index of the word in the whole text
            sentence_index (int) - index of the sentence this word belongs to

        In the case of the word "See", start: 0 and end: 3
        In the case of multiple analyses (for example many lemmas, many POS options),
        only choose the first for now.
    """

    text = Text(sentence["text"])

    word_summaries = []
    text.tag_layer()
    words = text.words
    word_spans_in_sentence = words[["start", "end"]]
    for i in range(len(words)):

        # Find the indexes of words in the whole text
        word_start_in_sentence = word_spans_in_sentence[i][0][0]
        start = sentence_span[0] + word_start_in_sentence
        end = start + len(words.text[i])

        # Find the sentence start and end indices
        sentence_start = sentence_span[0]
        sentence_end = sentence_span[1]

        # Find the lemma and pos of the word
        lemma = text.morph_analysis[i].lemma[0]
        pos = text.morph_analysis[i].partofspeech[0]

        word_summaries.append(
            {"text": words[i].text, "start": start, "end": end, "lemma": lemma,
             "pos": pos, "sentence_index": sentence_index,
             "sentence_start": sentence_start, "sentence_end": sentence_end})

    return word_summaries


def is_sentences_layer_necessary(config):
    return config.ANALYZE_OVERUSED_WORDS or config.ANALYZE_SENTENCE_LENGTH or \
        config.ANALYZE_IMPERSONALITY or config.ANALYZE_TAGS or config.ANALYZE_OFFICIALESE
