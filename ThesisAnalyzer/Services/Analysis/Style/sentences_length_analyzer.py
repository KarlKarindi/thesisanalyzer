# from ThesisAnalyzer import vabamorf
from ThesisAnalyzer.Services.Analysis.Style.Config import config
from ThesisAnalyzer.Models.Feedback import StyleFeedback
from ThesisAnalyzer.Services.utils import QuoteAnalyzer
from ThesisAnalyzer.Services import utils

from estnltk import Text, Layer
from estnltk.taggers import ClauseSegmenter, VerbChainDetector
from collections import defaultdict
from pprint import pprint

import statistics


class SentencesLengthSummary():

    def add_sent_to_long_sentences(self, sentence):
        """ Parameters:
                sentence (string) - string sentence to be added to list of long_sentences
        """
        self.long_sentences.append(sentence)

    def __init__(self):
        self.long_sentences = []


def analyze(text):
    """ Analyzes all the sentences and brings out all sentences that might be too long.
        On deciding on whether a sentence is long or not, see function is_sentence_too_long()
    """

    sentences = utils.get_sentences_layer(text)
    # Leave only the enclosing text
    sentences = [Text(sent.enclosing_text) for sent in sentences]

    sentencesLengthSummary = SentencesLengthSummary()

    # Initialize a ClauseSegmenter instance
    clause_segmenter = ClauseSegmenter()

    # Initalize a VerbChainDetector instance
    vc_detector = VerbChainDetector()

    # Initialize a QuoteAnalyzer instance
    quote_analyzer = QuoteAnalyzer()

    # Iterate through the sentences.
    for sentence in sentences:

        # Add the words layer to the sentence
        sentence.tag_layer(["words"])

        # Find the indexes of words and whether they are in quotes or not
        word_indexes_that_are_not_in_quotes = find_indexes_of_words_not_in_quotes(
            sentence, quote_analyzer)

        # Find clusters of words that are not in quotes
        clusters = dict(
            enumerate(create_clusters_of_viable_words(word_indexes_that_are_not_in_quotes)))

        # Create a clean sentence that doesn't have any quotes
        clean_sentence = create_clean_sentence(sentence, clusters)

        # If clean_sentence is empty, it's completely in quotes and shouldn't be analysed further.
        if len(clean_sentence.text) > 0:
            clauses = find_clauses_in_sentence(
                clean_sentence, clause_segmenter)

            clause_and_verb_chain_index = create_clause_and_verb_chain_index(
                clauses, vc_detector)

            sentence_is_long = is_sentence_too_long(
                clause_and_verb_chain_index, sentence)

            if sentence_is_long:
                sentencesLengthSummary.add_sent_to_long_sentences(
                    sentence.text)

    # Terminate the ClauseSegmenter process
    clause_segmenter.close()

    return sentencesLengthSummary


def find_indexes_of_words_not_in_quotes(sentence, quote_analyzer):
    """ Creates a list of word indexes that are not in quotes
        Parameters:
            sentence (Layer) - a sentence layer that has the words layer
        Returns:
            indexes_of_words_not_in_quotes (list) - list of word indexes that aren't in quotes
    """

    indexes_of_words_not_in_quotes = []

    for i, word in enumerate(sentence.words):
        in_quotes = quote_analyzer.is_word_in_quotes(word.text)
        if in_quotes is False:
            indexes_of_words_not_in_quotes.append(i)

    return indexes_of_words_not_in_quotes


def find_clauses_in_sentence(sentence, clause_segmenter):
    """ Segments the clauses (osalausestamine).
        Parameters:
            sentence (Layer) - one sentence as a Text object
            clause_segmenter (ClauseSegmenter) - ClauseSegmenter instance
        Returns:
            clauses (Layer) - the clauses layer for a sentence
     """
    # Tag clause annotations
    clause_segmenter.tag(sentence)
    return sentence.clauses


def create_clause_and_verb_chain_index(clauses, vc_detector):
    """ Creates an index of clauses.
        For each sentence, create a dictionary of clauses and
        the verb chains corresponding to those clauses.
        Parameters:
            clauses (Layer) - clauses layer
            vc_detector (VerbChainDetector) - VerbChainDetector instance
        Returns:
            clause_index_to_words (dict)
    """
    # Create a dictionary of the clauses and the words they consist of
    clause_and_verb_chain_index = defaultdict(list)

    for i, analysis in enumerate(clauses):
        clause_text_list = analysis.text
        verb_chains = find_verb_chain_in_clause(
            clause_text_list, vc_detector)

        clause_and_verb_chain_index[i] = {
            "verb_chains": verb_chains, "clause": clause_text_list}

    return clause_and_verb_chain_index


def find_verb_chain_in_clause(clause_text_list, vc_detector):
    """ Finds the verb chains in one singular clause.
        Parameters:
            clause_text_list (list) - list of words in one clause.
                Example: ["see", "peab", "saama", "tehtud"]
            vc_detector (VerbChainDetector) - instance of VerbChainDetector
        Returns:
            verb chains (string) - in the case of the example, it's "peab saama"
    """

    # Join all the words in clauses into one string
    clause_text = " ".join(clause_text_list)
    clause_text = Text(clause_text)

    # Clauses layer must be added
    clause_text.tag_layer(["clauses"])

    # Tag all the verb chains
    vc_detector.tag(clause_text)
    _verb_chains = clause_text.verb_chains

    return " ".join(_verb_chains.text)


def create_clusters_of_viable_words(word_indexes_that_are_not_in_quotes):
    """ Generator function that creates clusters of viable words.
        Viable words are words that aren't in quotes.
        Searches for words that aren't further away from each-other than 1 word
        Clustering function found here:
        https://stackoverflow.com/questions/15800895/finding-clusters-of-numbers-in-a-list
    """

    previous = None
    cluster = []
    for index in word_indexes_that_are_not_in_quotes:
        if not previous or index - previous == 1:
            cluster.append(index)
        else:
            yield cluster
            cluster = [index]
        previous = index
    if cluster:
        yield cluster


def create_clean_sentence(sentence, clusters):
    """ Creates a clean sentence that doesn't contain any words in quotes.
        Parameters:
            clusters (dict) - clusters of word spans where clusters are words next to each other
        Returns:
            clean_sentence (Text) - cleaned sentence without any quoted words.
            If a sentence is completely surrounded by quotes, clean_sentence.text is an empty string.
    """
    # Create a clean_sentence variable to later add to
    clean_sentence = ""

    # Iterate over all the clusters
    for i in range(len(clusters)):
        words = clusters[i]

        # Take the first and last index
        start = words[0]
        end = words[-1]

        # Add to the clean_sentence. Range is until n + 1, as n must be included
        clean_sentence += " " + sentence.words[start:end + 1].enclosing_text

    return Text(clean_sentence.strip()).tag_layer()


def is_sentence_too_long(clause_to_verb_chain_index, sentence):
    """ Analyzes the clauses in a sentence.
        Looks at clause word length, sentence word length, clause amount,
        returns feedback accordingly.

        Parameters:
            clauses (dict) - dictionary with clauses and verb chains in corresponding clauses
        Returns:
            boolean whether sentence is too long or not
    """

    total_clause_count = len(clause_to_verb_chain_index)
    verb_chains_count = 0
    for i in clause_to_verb_chain_index:
        verb_chains = clause_to_verb_chain_index[i]["verb_chains"]
        if len(verb_chains) > 0:
            verb_chains_count += 1

    half_of_clauses = total_clause_count // 2

    # TODO: Find optimal conditions that work the best
    # Conditions for deciding whether a sentence is too long
    if len(clause_to_verb_chain_index) > config.MAX_CLAUSE_AMOUNT and verb_chains_count > half_of_clauses:
        return True

    return False
