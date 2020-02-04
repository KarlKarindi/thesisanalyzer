from ThesisAnalyzer import vabamorf
from ThesisAnalyzer.Services.Constants import constants
from estnltk import Text


class AdverbSummary():

    def __init__(self, word_count, adverb_count):
        self.word_count = word_count
        self.adverb_count = adverb_count
        self.adverb_percentage = round(adverb_count / word_count, 2)


def analyze(text):
    """ Tags all the sentences and finds the percentage of adverbs (määrsõnad) """

    sentences = Text(text).sentence_texts

    adverb_count = 0
    total_count = 0
    tags = tag_words_in_sentences(sentences)

    for tag in tags:
        if tag == constants.ADVERB:
            adverb_count += 1
        total_count += 1

    adverbSummary = AdverbSummary(total_count, adverb_count)
    return adverbSummary


def tag_words_in_sentences(sentences):
    """ Tag all the words in a list of sentences using vabamorf
        Parameters:
            sentences - List of sentences
        Returns:
            list of tags
    """

    tags = []
    for sentence in sentences:
        sentence_analysis = vabamorf.analyze(sentence)
        for word in sentence_analysis:
            tag = word["analysis"][0]["partofspeech"]
            tags.append(tag)

    return tags
