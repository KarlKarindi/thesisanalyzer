# from ThesisAnalyzer import vabamorf
from ThesisAnalyzer.Services.Analysis.Style.Config import config
from ThesisAnalyzer.Models.Feedback import StyleFeedback
from ThesisAnalyzer.Services.utils import QuoteAnalyzer
from ThesisAnalyzer.Services import utils

from estnltk import Text
from estnltk.taggers import ClauseSegmenter, VerbChainDetector
from collections import defaultdict
from pprint import pprint

import statistics


class SentencesLengthSummary():

    def add_sent_to_long_sentences(self, sentence):
        self.long_sentences.append(sentence)

    def __init__(self):
        self.long_sentences = []


def analyze(text):

    sentences = utils.find_sentences(text)

    sentencesLengthSummary = SentencesLengthSummary()

    # Initialize a ClauseSegmenter instance
    clause_segmenter = ClauseSegmenter()

    quote_analyzer = QuoteAnalyzer()

    # Iterate through the sentences.
    # Create a clause_dict for every sentence, then check if sentence is too long.
    for sentence in sentences:
        clauses_dict = segment_clauses_in_sentence(
            sentence, clause_segmenter, quote_analyzer)

        # sentence_is_long = is_sentence_too_long(
        #   clauses_dict, sentence)

        # if sentence_is_long:
        #   sentencesLengthSummary.add_sent_to_long_sentences(sentence)

    # Terminate the ClauseSegmenter process
    clause_segmenter.close()

    return sentencesLengthSummary


def segment_clauses_in_sentence(sentence, clause_segmenter, quote_analyzer):
    """ Segments the clauses (osalausestamine).

        Parameters:
            sentence (String) - one sentence
            clause_segmenter - ClauseSegmenter instance
            quote_analyzer - QuoteAnalyzer instance
        Returns:
            dict with clauses and the verb chains.
            IMPORTANT: Verb chains are not taken into account if clause is in quotes
     """
    quote_analyzer.reset()

    # Tag clause annotations
    clause_segmenter.tag(sentence)
    clauses = sentence.clauses

    # Create a dictionary of the clauses and the words they consist of
    clause_indexes_to_words = defaultdict(list)

    # Create a set of indexes for words that are in quotes
    indexes_of_words_in_quotes = set()

    word_index = 0
    for clause_index, clause_analysis in enumerate(clauses):
        clause_text = clause_analysis.text
        pprint(clause_text)
        # Iterate over all the words in a clause
        for word in clause_text:
            in_quotes = quote_analyzer.is_word_in_quotes(word)

            # If a word is in quotes, don't add it into the clause, as it might be a title or quote.
            if not in_quotes:
                clause_indexes_to_words[clause_index].append(word)
            else:
                indexes_of_words_in_quotes.add(word_index)
            word_index += 1
    #

    # Find verb chains
    clauses_dict = map_clauses_to_verb_chains(
        sentence, clause_indexes_to_words, indexes_of_words_in_quotes)
    # return clauses_dict


def is_sentence_too_long(clauses, sentence):
    """ Analyzes the clauses in a sentence.
        Looks at clause word length, sentence word length, clause amount,
        returns feedback accordingly.

        Parameters:
            clauses (dict) - dictionary with clauses and verb chains in corresponding clauses
        Returns:
            boolean whether sentence is too long or not
    """

    total_clause_count = len(clauses)
    verb_chains_count = 0
    for i in clauses:
        verb_chains = clauses[i]["verb_chains"]
        if len(verb_chains) > 0:
            verb_chains_count += 1

    half_of_clauses = total_clause_count // 2

    # TODO: Find optimal conditions that work the best
    # Conditions for deciding whether a sentence is too long
    if len(clauses) > config.MAX_CLAUSE_AMOUNT and verb_chains_count > half_of_clauses:
        return True

    return False


def map_clauses_to_verb_chains(sentence, clause_indexes_to_words, indexes_of_words_in_quotes):
    """ Finds verb chains in the clauses of a sentence.

        Parameters:
            sentence (String) - string text of sentence
            clauses_indexes_to_words (dict) - dictionary of clause indexes in the
            sentence mapped to words (not in quotes)
        Returns: dict with clauses and the corresponding verb chains in clauses
    """
    vc_detector = VerbChainDetector()
    vc_detector.tag(sentence)
    verb_chains = sentence.verb_chains

    # Filtering. Leaves only the verb chains that aren't in quotes
    vc_analysis = [vc for vc in verb_chains if not set(
        vc.word_ids).issubset(indexes_of_words_in_quotes)]

    pprint(vc_analysis)
    


def map_clause_index_to_verb_chain_text(sentence, starts_ends):
    """ Parameters:
            sentence (String) - sentence in text form
            starts_ends - tuplet that has the clause_index, list of verb_chain_starts, list of verb_chain_ends
        Returns: dict that maps clause index to the verb chains (in text form)
    """

    clause_index_to_verb_chain = {}

    # Iterate through the list of tuplets, map clauses to their verb chains
    for cse in starts_ends:
        clause_index = cse[0]
        starts = cse[1]
        ends = cse[2]

        _verb_chain_texts = []
        for i in range(len(starts)):
            _verb_chain_texts.append(sentence[starts[i]:ends[i]])

        verb_chain = " ".join(_verb_chain_texts)
        clause_index_to_verb_chain[clause_index] = verb_chain

    return clause_index_to_verb_chain
