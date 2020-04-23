from ThesisAnalyzer.Models.Analysis import SentencesSummary, MissingCommas, SentenceWithMissingCommas, LongSentence
from ThesisAnalyzer.Services.Analysis.TextAnalyzers.analyzers import QuoteAnalyzer, CitationRemover, QuoteRemover
from ThesisAnalyzer.Services.Analysis import missing_commas_analyzer
from ThesisAnalyzer.Config import analysis as config
from ThesisAnalyzer.Services import utils
from ThesisAnalyzer.Constants import constants

from estnltk.taggers import ClauseSegmenter, VerbChainDetector
from estnltk import Text, Layer
from collections import defaultdict
from pprint import pprint
from copy import copy
import os

import re


def analyze(text, preprocessed_text, sentences_layer):
    """ Analyzes all the sentences and brings out all sentences that might be too long.
        On deciding on whether a sentence is long or not, see function is_sentence_too_long()
        Also checks whethere there are any missing commas in the text.
    """
    # Leave only the enclosing text
    sentences = [Text(sent.enclosing_text) for sent in sentences_layer]

    sentencesSummary = SentencesSummary()
    line_separator = os.linesep

    # Initialize ClauseSegmenter instances
    clause_segmenter_1 = ClauseSegmenter()
    clause_segmenter_2 = ClauseSegmenter()
    # Initialize a second ClauseSegmenter instance that ignores missing commas
    mc_clause_segmenter = ClauseSegmenter(ignore_missing_commas=True)

    # Initalize a VerbChainDetector instance
    vc_detector = VerbChainDetector()

    quote_analyzer = QuoteAnalyzer()
    quote_remover = QuoteRemover()
    citation_remover = CitationRemover()

    # Iterate through the sentences.
    for i, sentence in enumerate(sentences):

        sentence.tag_layer()

        # Find the indexes of words and whether they are in quotes or not
        indexes_of_words_not_in_quotes = quote_analyzer.find_indexes_of_words_not_in_quotes(sentence)

        # Find clusters of words that are not in quotes
        clusters = dict(enumerate(
            quote_analyzer.create_clusters_of_words_not_in_quotes(indexes_of_words_not_in_quotes)))

        # Create a sentence text that doesn't have any quotes
        sentence_text_without_quotes = quote_remover.remove_quoted_parts_from_sentence(
            sentence, clusters)

        sentence_text_without_noise = remove_noise_from_sentence(sentence_text_without_quotes, line_separator)

        cleaned_sentence = citation_remover.get_sentence_without_citations(
            sentence_text_without_noise)

        # If sentence_text_without_quotes is empty, it's completely in quotes and shouldn't be analysed further.
        if len(sentence_text_without_quotes) > 0:
            # Create a copy of the cleaned sentence before it's tagged by the clause segmenter
            sentence_copy = copy(sentence)

            clause_segmenter_1.tag(sentence)
            # Use the normal clause segmenter
            clauses = sentence.clauses
            clause_and_verb_chain_index = create_clause_and_verb_chain_index(clauses, vc_detector)
            clause_positions_original = clauses[["start", "end"]]

            # Use the clause segmenter that ignores missing commas to check for comma errors
            sentence_with_missing_comma = missing_commas_analyzer.get_sentence_with_missing_comma(
                i, mc_clause_segmenter, vc_detector, sentence_copy,
                clause_and_verb_chain_index, preprocessed_text)

            if sentence_with_missing_comma is not None:
                sentencesSummary.sentences_with_missing_commas.append(sentence_with_missing_comma)

            clause_segmenter_2.tag(cleaned_sentence)
            cleaned_clauses = cleaned_sentence.clauses
            cleaned_clause_and_verb_chain_index = create_clause_and_verb_chain_index(
                cleaned_clauses, vc_detector, keep_parentheses_without_verb_chains=False)

            sentence_is_long = is_sentence_too_long(cleaned_clause_and_verb_chain_index)
            if sentence_is_long:
                # Add the sentence dictionary from the preprocessed_text.sentences, contains position info and text.

                longSentence = LongSentence(preprocessed_text.sentences[i], clause_positions_original)
                sentencesSummary.long_sentences.append(longSentence)

    # Terminate the ClauseSegmenter processes
    clause_segmenter_1.close()
    clause_segmenter_2.close()
    mc_clause_segmenter.close()

    return sentencesSummary


def remove_noise_from_sentence(sentence, line_separator):
    """ Removes any unnecessary noise from the sentence that might trigger a long sentence warning.
        For example when a picture caption or header doesn't have a period at the end of it,
        it will join with the next sentence.
        Parameters:
            sentence (string) - sentence in string form with quotes removed
            line_separator (string) - OS specific line separator
        Returns:
            string sentence
    """

    sentence_split_by_new_line = sentence.split(line_separator)
    if len(sentence_split_by_new_line) > 1:
        # Check the last char before the linebreak
        if sentence_split_by_new_line[0][-1] != ".":
            return sentence_split_by_new_line[-1]
    return sentence


def create_clause_and_verb_chain_index(clauses, vc_detector, keep_parentheses_without_verb_chains=True):
    """ Creates an index of clauses.
        For each sentence, create a dictionary of clauses and
        the verb chains corresponding to those clauses.
        Parameters:
            clauses (Layer) - clauses layer
            vc_detector (VerbChainDetector) - VerbChainDetector instance
            keep_parentheses_without_verb_chains (boolean) - If set to false, will ignore
                                                             parentheses without verb chains.
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

        if keep_parentheses_without_verb_chains or do_add:
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

    # Conditions for deciding whether a sentence is too long
    if total_clause_count > config.MAX_CLAUSE_AMOUNT and verb_chains_count >= 2:
        return True

    return False
