from ThesisAnalyzer import vabamorf
from ThesisAnalyzer.Services.Analysis.Style.Config import config
from ThesisAnalyzer.Models.Feedback import StyleFeedback
from ThesisAnalyzer.Services import utils

from estnltk import Text, ClauseSegmenter
from collections import defaultdict
from pprint import pprint

import statistics


def analyze(text):
    """ Function to start the clause analysis """
    sentences = Text(text).sentence_texts

    segmenter = ClauseSegmenter()

    for sentence in sentences:
        clauses = segment_clauses_in_sentence(sentence, segmenter)
        clauses_feedback = analyze_clauses_in_sentence(
            clauses, sentence)
    return None


def analyze_clauses_in_sentence(clauses, sentence):
    """ Analyzes the clauses in a sentence.
        Looks at clause word length, sentence word length, clause amount,
        returns feedback accordingly.

        Parameters:
            clauses (dict) - dictionary with clauses
        Returns:
            feedback - StyleFeedback object
    """
    feedback = StyleFeedback()

    # pprint(sentence)
    # pprint(clauses)
    # Count all the words in clauses
    total_word_count = 0
    clause_lengths = []
    for clause in clauses.values():
        clause_word_count = len(clause)
        total_word_count += clause_word_count
        clause_lengths.append(clause_word_count)
        # print("CLAUSE_LEN", clause_word_count)

    mean_word_count_in_clauses = total_word_count / len(clauses)
    median_word_count_in_clauses = statistics.median(
        clause_lengths)

    # print("MEAN_WORD_COUNT_IN_CLAUSE", mean_word_count_in_clauses)
    # print("MEDIAN_WORD_COUNT_IN_CLAUSE", median_word_count_in_clauses)
    # print("WORD_COUNT", total_word_count)
    # print()

    # FIXME: Kui on loetelu, milles on nt pealkirjad vms, siis vaata, mida teha. Sama tsitaatidega.
    if len(clauses) > config.MAX_CLAUSE_AMOUNT:
        print('Lause\n"' + sentence +
              '"\ntundub liiga pikk. Võimalik, et seda saab lühemaks teha.')

    # Äkki on võimalik teha osalause võrdlust? Näiteks vaadata osalausete sõnaarvu mediaani
    # ning vaadata, kas mingi osalause erineb sellest väga palju.

    return feedback


def segment_clauses_in_sentence(sentence, segmenter):
    """ Segments the clauses (osalausestamine)

        Parameters:
            sentence (String) - one sentence
            segmenter - ClauseSegmenter
        Returns:
            dict with clauses and the verb chains
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
    clauses_summary = map_clauses_to_verb_chains(sentence, clauses)

    pprint(clauses_summary)
    return clauses


def map_clauses_to_verb_chains(sentence, clauses):
    """ Finds verb chains in the clauses of a sentence.
        Parameters:
            sentence (String) - string text of sentence
            clauses (dict) - dictionary of clauses in the sentence (not in quotes)
        Returns: dict with clauses and the corresponding verb chains in clauses
    """

    text = Text(sentence).tag_verb_chains()

    # Filter
    vc_analysis = [
        vc for vc in text.verb_chains if vc["clause_index"] in clauses.keys()]

    # Create a list of tuplets (clause_index, list of verb chain starts, list of verb chain ends)
    starts_ends = [(vc["clause_index"], vc["start"], vc["end"])
                   for vc in vc_analysis]

    # Create a dictionary that maps clause indexes to verb chains
    clause_index_to_verb_chain = map_clause_index_to_verb_chain_text(
        sentence, starts_ends)

    # Create a dictionary that combines the clauses with the verb chains in them
    clauses_summary = {}
    for i in clauses:
        if i in clause_index_to_verb_chain.keys():
            verb_chains = [clause_index_to_verb_chain[i]]
        else:
            verb_chains = []

        clauses_summary[i] = {
            "words": clauses[i], "verb_chains": verb_chains}

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
