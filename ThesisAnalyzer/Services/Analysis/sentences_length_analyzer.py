from ThesisAnalyzer.Config import analysis as config
from ThesisAnalyzer.Services.Analysis.TextAnalyzers.analyzers import QuoteAnalyzer, CitationAnalyzer
from ThesisAnalyzer.Services import utils
from ThesisAnalyzer.Models.Analysis import SentencesLengthSummary

from estnltk.taggers import ClauseSegmenter, VerbChainDetector
from estnltk import Text, Layer
from collections import defaultdict
from pprint import pprint
from copy import copy

import re


def analyze(text, sentences_layer):
    """ Analyzes all the sentences and brings out all sentences that might be too long.
        On deciding on whether a sentence is long or not, see function is_sentence_too_long()
    """
    # Leave only the enclosing text
    sentences = [Text(sent.enclosing_text) for sent in sentences_layer]

    sentencesLengthSummary = SentencesLengthSummary()

    # Initialize a ClauseSegmenter instance
    clause_segmenter = ClauseSegmenter()
    # Initialize a second ClauseSegmenter instance that ignores missing commas
    clause_segmenter_that_ignores_missing_commas = ClauseSegmenter(ignore_missing_commas=True)

    # Initalize a VerbChainDetector instance
    vc_detector = VerbChainDetector()

    # Initialize a QuoteAnalyzer instance
    quote_analyzer = QuoteAnalyzer()

    citation_analyzer = CitationAnalyzer()

    # Iterate through the sentences.
    for sentence in sentences:

        # Add the words layer to the sentence
        sentence.tag_layer(["words"])

        # Find the indexes of words and whether they are in quotes or not
        word_indexes_that_are_not_in_quotes = find_indexes_of_words_not_in_quotes(
            sentence, quote_analyzer)

        # Find clusters of words that are not in quotes
        clusters = dict(
            enumerate(create_clusters_of_words_not_in_quotes(word_indexes_that_are_not_in_quotes)))

        # Create a sentence text that doesn't have any quotes
        sentence_text_without_quotes_unchecked = remove_quoted_parts_from_sentence(
            sentence, clusters)

        cleaned_sentence = citation_analyzer.get_sentence_without_citations(
            sentence_text_without_quotes_unchecked)

        # If sentence_text_without_quotes is empty, it's completely in quotes and shouldn't be analysed further.
        if len(sentence_text_without_quotes_unchecked) > 0:
            # Create a copy of the cleaned sentence before it's tagged by the clause segmenter
            cleaned_sentence_copy = copy(cleaned_sentence)

            clauses = find_clauses_in_sentence(cleaned_sentence, clause_segmenter)

            clause_and_verb_chain_index = create_clause_and_verb_chain_index(clauses, vc_detector)

            clauses_using_missing_commas_segmenter = find_clauses_in_sentence(
                cleaned_sentence_copy, clause_segmenter_that_ignores_missing_commas)
            clause_and_verb_chain_index_with_missing_commas = create_clause_and_verb_chain_index(
                clauses_using_missing_commas_segmenter, vc_detector)

            # if len(clause_and_verb_chain_index_with_missing_commas) > len(clause_and_verb_chain_index):
            #     print(sentence.text)
            #     pprint(clause_and_verb_chain_index)
            #     print("------")
            #     pprint(clause_and_verb_chain_index_with_missing_commas)

            #     print("\n\n==========\n\n")

            sentence_is_long = is_sentence_too_long(clause_and_verb_chain_index)

            if sentence_is_long:
                sentencesLengthSummary.add_sent_to_long_sentences(sentence.text)

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

        do_add = True
        if clause_text_list[0] == "(" and clause_text_list[-1] == ")":
            # If the clause is in parentheses and doesn't contain a verb, don't take it into account
            if len(verb_chains) == 0:
                do_add = False

        if do_add:
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


def create_clusters_of_words_not_in_quotes(word_indexes_that_are_not_in_quotes):
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


def remove_quoted_parts_from_sentence(sentence, clusters):
    """ Creates a clean sentence that doesn't contain any words in quotes.
        Parameters:
            sentence (Text) - Text object
            clusters (dict) - clusters of word spans where clusters are words next to each other
        Returns:
            clean_sentence (string) - cleaned sentence text without any quoted words.
            If a sentence is completely surrounded by quotes, clean_sentence is an empty string.
    """
    # Create a clean_sentence variable to later add to
    clean_sentence = ""

    # Iterate over all the clusters
    for i in range(len(clusters)):
        words = clusters[i]
        print(words)

        # Take the first and last index
        start = words[0]
        end = words[-1]

        # Add to the clean_sentence. Range is until n + 1, as n must be included
        clean_sentence += " " + sentence.words[start:end + 1].enclosing_text

    print()
    print("SIIN")
    print(clean_sentence)
    print()
    print()

    return clean_sentence.strip()


def is_sentence_too_long(clause_and_verb_chain_index):
    """ Analyzes the clauses in a sentence.
        Looks at clause word length, sentence word length, clause amount,
        returns feedback accordingly.

        Parameters:
            clause_to_verb_chain_index (dict) - dictionary with clauses and verb chains in corresponding clauses
        Returns:
            boolean whether sentence is too long or not
    """

    total_clause_count = len(clause_and_verb_chain_index)
    verb_chains_count = 0
    for i in clause_and_verb_chain_index:
        verb_chains = clause_and_verb_chain_index[i]["verb_chains"]
        if len(verb_chains) > 0:
            verb_chains_count += 1

    half_of_clauses = total_clause_count // 2

    # TODO: Find optimal conditions that work the best
    # Conditions for deciding whether a sentence is too long
    if total_clause_count > config.MAX_CLAUSE_AMOUNT and verb_chains_count >= 2:
        return True

    # If 5 or mmore clauses and at least 4 verbs
    # if total_clause_count >= 5 and total_clause_count - verb_chains_count <= 1:
        # return True

    return False
