class PreprocessedText(object):
    """ Container object for preprocessed text information. """

    def __init__(self, sentences, words, sentence_words):
        self.sentences = sentences
        self.words = words
        self.sentence_words = sentence_words
