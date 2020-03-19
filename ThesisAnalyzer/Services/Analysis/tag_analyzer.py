#from ThesisAnalyzer import vabamorf
from ThesisAnalyzer.Services.Constants import constants
from estnltk import Text
from pprint import pprint


class TagSummary():

    def __init__(self, word_count, adverb_count, pronoun_count):
        self.word_count = word_count
        self.adverb_count = adverb_count
        self.adverb_percentage = round(adverb_count / word_count, 3)
        self.pronoun_count = pronoun_count
        self.pronoun_percentage = round(pronoun_count / word_count, 3)


def analyze(text):
    """ Tags all the sentences and finds the percentage of certain types of words.
        Looks for adverbs (määrsõnad) and pronouns (asesõnad).
        Returns: TagSummary object
    """

    sentences = Text(text).sentence_texts

    tags = tag_words_in_sentences(sentences)

    total_count, adverb_count, pronoun_count = 0, 0, 0

    for n in tags:
        tag = n[1]

        if tag == constants.ADVERB:
            adverb_count += 1
        elif tag == constants.PRONOUN:
            pronoun_count += 1

        total_count += 1

    tagSummary = TagSummary(total_count, adverb_count, pronoun_count)
    return tagSummary


def tag_words_in_sentences(sentences):
    """ Tag all the words in a list of sentences using vabamorf.

        Parameters:
            sentences (list) - list of sentences
        Returns:
            list of tuplets (word, tag)
    """

    tags = []
    for sentence in sentences:
        sentence_analysis = vabamorf.analyze(sentence)
        for word in sentence_analysis:
            text = word["text"]
            tag = word["analysis"][0]["partofspeech"]
            tags.append((text, tag))

    return tags
