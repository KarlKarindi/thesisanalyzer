from ThesisAnalyzer.Models.Preprocess import PreprocessedText
from estnltk import Text


def preprocess_text(original_text, sentences_layer):
    """ Preprocesses the text, calls out the functions
        find_sentences_with_index_and_span() and get_words_in_sentence()
        Parameters:
            original_text (string) - A string of the original text
            sentences_layer (Layer) - The Text.sentences layer
        Returns:
            sentences (dict) - output of find_sentences_with_index_and_span()
            words (dict) - output of get_words_in_sentence()
            sentence_words (dict) - index of sentences with the words in them
    """

    sentence_words = {}
    sentences = create_dict_of_sentences(original_text, sentences_layer)
    words = []

    sentence_index = 0  # Necessary in case there are no sentences
    for index, sentence in sentences.items():
        __words = get_words_in_sentence(sentence, index)
        words.extend(__words)
        sentence_words[sentence_index] = __words
        sentence_index += 1

    return PreprocessedText(sentences, words, sentence_words)


def create_dict_of_sentences(text, sentences_layer):
    """ Returns: dictionary with index as key and text and position as values """

    keys, values = [], []

    sentence_spans = sentences_layer[["start", "end"]]

    for i, sentence in enumerate(sentences_layer):
        start = sentence_spans[i][0]
        end = sentence_spans[i][1]
        values.append({"position": [start, end], "text": sentence.enclosing_text, "sentence_index": i})
        keys.append(i)

    return dict(zip(keys, values))


def get_words_in_sentence(sentence, sentence_index):
    """ Returns a list of all words in a sentence.
        Words in this case are dictionaries that have attributes:
            text (string) - text string of the word
            pos (string) - part of speech of the word
            lemma (string) - lemma of the word
            position (list) - [start, end] position of the word in the original text
            sentence_index (int) - index of the sentence this word belongs to
            sentence_position [list] - [start, end] position of the sentence

        In the case of the word "See", start: 0 and end: 3
        In the case of multiple analyses (for example many lemmas, many POS options),
        only choose the first for now.
    """

    text = Text(sentence["text"])
    sentence_span = sentence["position"]

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
            {"text": words[i].text, "position": [start, end], "lemma": lemma,
             "pos": pos, "sentence_index": sentence_index,
             "sentence_position": [sentence_start, sentence_end]})

    return word_summaries
