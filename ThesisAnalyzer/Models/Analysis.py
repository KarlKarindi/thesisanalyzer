# This module contains classes for analysis

# _____________________________________ #
#        Impersonality analyzer         #


class ImpersonalitySummary():

    def __init__(self, is_impersonal, sentences_with_pv):
        self.is_impersonal = is_impersonal
        self.sentences_with_pv = sentences_with_pv

# _____________________________________ #
#        Overused Word analyzer         #


class TextSummmary(object):
    """ Container class for OverusedWordSummary object """

    def __init__(self, word_count, sentence_count, OverusedWordSummary):
        self.word_count = word_count
        self.sentence_count = sentence_count
        self.overused_word_summary = OverusedWordSummary


class OverusedWordSummary(object):
    """ Container object for word usage analysis. """

    # Adds another cluster to the summary's list of clusters.
    def add_cluster(self, cluster):
        self.clusters.extend(cluster)

    def __init__(self, lemma, words_in_text, multiplier):
        """ On initialization, don't find the synonyms.
            Finding synonyms gets called out only on the top 20 most overused words
        """

        self.multiplier = multiplier
        self.lemma = lemma
        # Create a list from the set of words_in_text, then sort it by start index.
        words = [key for key in words_in_text]
        self.words = sorted(words, key=lambda x: x.position[0], reverse=False)
        self.times_used = len(self.words)
        self.words_synonyms = []
        self.lemma_synonyms = []
        self.clusters = []

    def __repr__(self):
        return self.lemma


class WordSummary(object):

    def __init__(self, text, part_of_speech, position, sentence_index, sentence_position,
                 id=None, cluster_index=None, position_in_cluster=None):
        # Not initialized on start. Corresponds to it's index in the OverusedWordSummary words list.
        self.id = id
        self.text = text
        self.part_of_speech = part_of_speech
        self.position = position
        self.sentence_index = sentence_index
        self.sentence_position = sentence_position
        self.cluster_index = cluster_index  # Not initalized on start.
        # Not initalized on start.
        self.position_in_cluster = position_in_cluster

    def __repr__(self):
        return '<Word (id, {}, text: {}, part_of_speech: {}, position: [{}, {}], sentence_index: {}, sentence_position: \
             [{}, {}])>'.format(self.id, self.text, self.part_of_speech, self.position[0], self.position[1],
                                self.sentence_index, self.sentence_position[0], self.sentence_position[1])


class ClusterContainer(object):
    """ Used for containing cluster information """

    def __init__(self, text, start, end):
        self.text = text
        self.sentence_position = [start, end]
        self.word_indexes = []

    def __repr__(self):
        return '<ClusterContainer (sentence_position: [{}, {}], text: {})'.format(self.sentence_position[0],
                                                                                  self.sentence_position[1], self.text)


# _____________________________________ #
#       Sentence length analyzer        #


class SentencesLengthSummary():

    def add_sent_to_long_sentences(self, sentence):
        """ Parameters:
                sentence (string) - string sentence to be added to list of long_sentences
        """
        self.long_sentences.append(sentence)

    def __init__(self):
        self.long_sentences = []


# _____________________________________ #
#           Tag analyzer                #

class TagSummary():

    def __init__(self, word_count, adverb_count, pronoun_count):
        self.adverb_count = adverb_count
        self.pronoun_count = pronoun_count

        if word_count > 0:
            self.adverb_percentage = round(adverb_count / word_count, 3)
            self.pronoun_percentage = round(pronoun_count / word_count, 3)
        else:
            self.adverb_percentage = 0
            self.pronoun_percentage = 0
