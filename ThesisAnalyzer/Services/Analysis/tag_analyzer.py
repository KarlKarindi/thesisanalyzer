from ThesisAnalyzer.Models.Analysis import TagSummary
from ThesisAnalyzer.Constants import constants
from estnltk import Text
from pprint import pprint


def analyze(text, text_obj, word_count):
    """ Tags all the sentences and finds the percentage of certain types of words.
        Looks for adverbs (määrsõnad) and pronouns (asesõnad).
        Returns: TagSummary object
    """

    morph_analysis = text_obj.morph_analysis

    adverb_count, pronoun_count = 0, 0

    for n in morph_analysis:
        tag = n["partofspeech"][0]

        if tag == constants.ADVERB:
            adverb_count += 1
        elif tag == constants.PRONOUN:
            pronoun_count += 1

    tagSummary = TagSummary(word_count, adverb_count, pronoun_count)
    return tagSummary
