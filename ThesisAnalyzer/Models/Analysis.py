# This module contains classes for analysis

# _____________________________________ #
#        Impersonality analyzer         #


class ImpersonalitySummary():

    def __init__(self, is_impersonal, sentences_with_pv):
        self.is_impersonal = is_impersonal
        self.sentences_with_pv = sentences_with_pv

# _____________________________________ #
#        Overused Word analyzer         #


class TextSummmary():
    """ Container class for OverusedWordSummary object """

    def __init__(self, word_count, sentence_count, OverusedWordSummary):
        self.word_count = word_count
        self.sentence_count = sentence_count
        self.overused_word_summary = OverusedWordSummary


class OverusedWordSummary():
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


class WordSummary():

    def __init__(self, text, part_of_speech, position, sentence_index, sentence_position,
                 id=None, cluster_index=None, position_in_cluster=None):
        # Id is not initialized on start. Corresponds to it's index in the OverusedWordSummary words list
        self.id = id
        self.text = text
        self.part_of_speech = part_of_speech
        self.position = position
        self.sentence_index = sentence_index
        self.sentence_position = sentence_position

        # Following are not initalized on start
        self.cluster_index = cluster_index
        self.position_in_cluster = position_in_cluster

    def __repr__(self):
        return '<Word (id, {}, text: {}, part_of_speech: {}, position: [{}, {}], sentence_index: {}, sentence_position: \
             [{}, {}])>'.format(self.id, self.text, self.part_of_speech, self.position[0], self.position[1],
                                self.sentence_index, self.sentence_position[0], self.sentence_position[1])


class ClusterContainer():
    """ Used for containing cluster information """

    def __init__(self, text, start, end):
        self.text = text
        self.sentence_position = [start, end]
        self.word_indexes = []

    def __repr__(self):
        return '<ClusterContainer (sentence_position: [{}, {}], text: {})'.format(self.sentence_position[0],
                                                                                  self.sentence_position[1], self.text)


# _____________________________________ #
#           Sentences analyzer          #


class SentencesSummary():

    def __init__(self):
        self.long_sentences = []
        self.sentences_with_missing_commas = []


class LongSentence():

    def __init__(self, sentence_information, clause_positions):
        self.text = sentence_information["text"]
        self.position = sentence_information["position"]
        self.clause_positions = [[clause_pos[0], clause_pos[1]] for clause_pos in clause_positions]


class SentenceWithMissingCommas():

    def __init__(self, sentence_information, missing_commas, clause_positions):
        # missing_commas is an instance of MissingComma
        self.text = sentence_information["text"]
        self.position = sentence_information["position"]
        self.missing_comma_positions_in_sentence = missing_commas.comma_positions_in_sentence
        self.clauses_after_missing_comma = missing_commas.following_clauses
        self.clause_positions = [[clause_pos[0], clause_pos[1]] for clause_pos in clause_positions]


class MissingCommas():
    def __init__(self, comma_positions_in_sentence, following_clauses):
        # Both fields are lists
        self.comma_positions_in_sentence = comma_positions_in_sentence
        self.following_clauses = following_clauses

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

# _____________________________________ #
#         Officialese analyzer          #


class OfficialeseSummary():
    def __init__(self):
        self.poolt_tarind_summary = []
        self.maarus_saavas_summary = []
        self.olema_kesksona_summary = []
        self.nominalisatsioon_mine_vormis_summary = []


class NormalTextSliceContainer():
    """ Contains text slices that should be marked in bold for the user form.
        The text slice will be bold from start to finish.
    """

    def __init__(self, sentence_text, sentence_position, text, position):
        self.sentence_text = sentence_text
        self.sentence_position = sentence_position
        self.text = text
        self.position = position

    def __repr__(self):
        return '<NormalTextSliceContainer (text: {}, sentence_text: {}, sentence_position: {}, position: {})>' \
            .format(self.text, self.sentence_text, self.sentence_position, self.position)


class ParentChildContainer():
    """ Contains parent and child word positions in the text.
        Used to bold words that might not be connected to each other.
    """

    def __init__(self, sentence_text, sentence_position, parent_position, child_position, parent_text, child_text):
        self.sentence_text = sentence_text
        self.sentence_position = sentence_position
        self.parent_position = parent_position
        self.child_position = child_position
        self.parent_text = parent_text
        self.child_text = child_text

    def __repr__(self):
        return '<ParentChildContainer (sentence_text: {}, sentence_position: {}, parent_position: {}, ' \
            'parent_text: {}, child_position: {}, child_text: {})>' \
            .format(self.sentence_text, self.sentence_position, self.parent_position,
                    self.parent_text, self.child_position, self.child_text)
