from ThesisAnalyzer import vabamorf
from ThesisAnalyzer.Services.Analysis.Style.Config import config
from ThesisAnalyzer.Models.Feedback import StyleFeedback
from ThesisAnalyzer.Services import utils

from estnltk import Text, ClauseSegmenter
from collections import defaultdict
from pprint import pprint

import statistics


class ClauseSummary():

    def add_sent_to_long_sentences(self, sentence):
        self.long_sentences.append(sentence)

    def __init__(self):
        self.long_sentences = []


def analyze(text):

    sentences = Text(text).sentence_texts

    segmenter = ClauseSegmenter()

    clauseSummary = ClauseSummary()

    # Iterate through the sentences.
    # Create a clause_dict for every sentence, then check if sentence is too long.
    for sentence in sentences:
        clauses_dict = segment_clauses_in_sentence(sentence, segmenter)
        sentence_is_long = is_sentence_too_long(
            clauses_dict, sentence)

        if sentence_is_long:
            clauseSummary.add_sent_to_long_sentences(sentence)

    return clauseSummary


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


def segment_clauses_in_sentence(sentence, segmenter):
    """ Segments the clauses (osalausestamine).

        Parameters:
            sentence (String) - one sentence
            segmenter - ClauseSegmenter
        Returns:
            dict with clauses and the verb chains.
            IMPORTANT: Verb chains are not taken into account if clause is in quotes
     """

    # The sentence must be morphologically analyzed and then segmented.
    prepared = vabamorf.analyze(sentence)
    segmented = segmenter.mark_annotations(prepared)

    # Create a dictionary of the clauses and the words they consist of.
    clauses = defaultdict(list)

    in_quotes = False
    previous_word = None

    for word_analysis in segmented:
        word = word_analysis["text"]
        in_quotes = utils.is_word_in_quotes(word, previous_word, in_quotes)
        previous_word = word

        if not in_quotes:
            clause_index = word_analysis["clause_index"]
            clauses[clause_index].append(word)

    # Find verb chains
    clauses_dict = map_clauses_to_verb_chains(sentence, clauses)

    return clauses_dict


def map_clauses_to_verb_chains(sentence, clauses_not_in_quotes):
    """ Finds verb chains in the clauses of a sentence.

        Parameters:
            sentence (String) - string text of sentence
            clauses (dict) - dictionary of clauses in the sentence (not in quotes)
        Returns: dict with clauses and the corresponding verb chains in clauses
    """

    text = Text(sentence).tag_verb_chains()

    # Filter. Leave only the verb chains analyses that aren't in quotes
    vc_analysis = [
        vc for vc in text.verb_chains if vc["clause_index"] in clauses_not_in_quotes.keys()]

    # Create a list of tuplets (clause_index, list of verb chain starts, list of verb chain ends)
    starts_ends = [(vc["clause_index"], vc["start"], vc["end"])
                   for vc in vc_analysis]

    # Create a dictionary that maps clause indexes to verb chains
    clause_index_to_verb_chain = map_clause_index_to_verb_chain_text(
        sentence, starts_ends)

    # Create a dictionary that combines the clauses with the verb chains in them
    clauses_summary = {}
    for i in clauses_not_in_quotes:
        # If clause contains verb chains, add the verb chains as values
        if i in clause_index_to_verb_chain.keys():
            verb_chains = [clause_index_to_verb_chain[i]]
        else:  # Add an empty list as the verb chains
            verb_chains = []

        clauses_summary[i] = {
            "words": clauses_not_in_quotes[i], "verb_chains": verb_chains}

    return clauses_summary


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
