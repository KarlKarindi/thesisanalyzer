from ThesisAnalyzer import vabamorf
from ThesisAnalyzer.Services.Constants import constants
from estnltk import Text


def analyze(text):
    """ Tags all the sentences and finds the percentage of adverbs(määrsõnad) """

    sentences = Text(text).sentence_texts

    adverb_count = 0
    total_count = 0
    tags = tag_words_in_sentences(sentences)

    for tag in tags:
        if tag == constants.ADVERB:
            adverb_count += 1
        total_count += 1

    adverb_percentage = round(
        (adverb_count / total_count) * 100, 2)
    print("Total count:", total_count)
    print("Adverb count:", adverb_count)
    print("Adverb percentage is",
          str(adverb_percentage) + "%")


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
