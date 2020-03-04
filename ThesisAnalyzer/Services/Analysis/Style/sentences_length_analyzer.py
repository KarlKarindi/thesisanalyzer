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

    sentences = utils.find_sentences(text)
    sentencesLengthSummary = SentencesLengthSummary()

    # Initialize a ClauseSegmenter instance
    clause_segmenter = ClauseSegmenter()
    vc_detector = VerbChainDetector()
    quote_analyzer = QuoteAnalyzer()

    # Iterate through the sentences.
    # Create a clause_dict for every sentence, then check if sentence is too long.
    for sentence in sentences:
        sentence = add_word_info_layer_to_sentence(
            sentence, quote_analyzer)

        # TODO: Leave only the non-quoted parts of a sentence. indexof
        # Find the start and end indexes of quotes
        words_not_in_quotes = sentence.words.groupby(
            ["in_quotes"], return_type="spans")

        # pprint(words_not_in_quotes.groups[(False,)])

        # cleaned_sentence = get_sentence_without_quotes(sentence,
        #                                              quote_end_indexes, quote_start_indexes)

        #print("SIIN ON VASTUS\n", sentence.words[0:4].enclosing_text)

        # print(cleaned_sentence)

        print()

        clauses = find_clauses_in_sentence(
            sentence, clause_segmenter)

        verb_chain_to_clause = find_verb_chain_for_clauses(
            clauses, vc_detector)

        sentence_is_long = is_sentence_too_long(verb_chain_to_clause, sentence)

        if sentence_is_long:
            sentencesLengthSummary.add_sent_to_long_sentences(sentence.text)

    # Terminate the ClauseSegmenter process
    clause_segmenter.close()

    return sentencesLengthSummary


def add_word_info_layer_to_sentence(sentence, quote_analyzer):
    """ Adds a word_info layer to the sentence Text object.
        word_info layer contains attributes:
            word_id - index of the word in a sentence.
            in_quotes - whether the word is in quotes or not.
     """

    # Save a temporary list that contains all the words
    temp_words = [word for word in sentence.words]
    temp_normalized_forms = [
        nf.normalized_form[0] for nf in sentence.words]

    # Delete the words layer to later replace it
    del sentence.words

    # Add a custom words layer
    words = Layer(name="words",
                  attributes=["id", "in_quotes", "normalized_form"]
                  )
    sentence.add_layer(words)

    # Populate the layer
    for i, word in enumerate(temp_words):
        word_text = word.text
        in_quote = quote_analyzer.is_word_in_quotes(word_text)
        words.add_annotation(word, id=i, in_quotes=in_quote,
                             normalized_form=temp_normalized_forms[i])

    sentence.tag_layer(["sentences", "morph_analysis"])

    return sentence


def find_clauses_in_sentence(sentence, clause_segmenter):
    """ Segments the clauses (osalausestamine).
        # TODO: UPDATE
        Parameters:
            sentence (String) - one sentence
            clause_segmenter - ClauseSegmenter instance
            quote_analyzer - QuoteAnalyzer instance
        Returns:
            dict with clauses and the verb chains.
            IMPORTANT: Verb chains are not taken into account if clause is in quotes
     """
    # Tag clause annotations
    clause_segmenter.tag(sentence)
    clauses = sentence.clauses

    # CLAUSES.ENCLOSINGTEXT

    return clauses


def find_verb_chain_for_clauses(clauses, vc_detector):
    # Create a dictionary of the clauses and the words they consist of
    clause_index_to_words = defaultdict(list)

    # Iterate over all the words and find whether they are in quotes or not. If not, add to clauses to analyse

    # print()

    for i, analysis in enumerate(clauses):
        # What about enclosing text?
        clause_text_list = analysis.text
        verb_chains = find_verb_chain_in_clause(
            clause_text_list, vc_detector)

        clause_index_to_words[i] = {
            "verb_chains": verb_chains, "clause": clause_text_list}

    return clause_index_to_words


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


def find_verb_chain_in_clause(clause_text_list, vc_detector):

    clause_text = " ".join(clause_text_list)

    clause_text = Text(clause_text)

    # Clauses layer must be added
    clause_text.tag_layer(["clauses"])

    vc_detector.tag(clause_text)

    _verb_chains = clause_text.verb_chains

    return " ".join(_verb_chains.text)


def find_quote_status_change_indexes(sentence):
    previous_status = None
    quote_end_indexes = []
    quote_start_indexes = []
    for word in sentence.words:

        if previous_status is False and word.in_quotes is True:
            quote_start_indexes.append(word.id)

        if previous_status is True and word.in_quotes is False:
            quote_end_indexes.append(word.id)

        # For the first word of the sentence, decide if quotes start or not
        if previous_status is None:
            if word.in_quotes is True:
                quote_start_indexes.append(word.id)
            elif word.in_quotes is False:
                quote_end_indexes.append(word.id)

        previous_status = word.in_quotes

    return quote_end_indexes, quote_start_indexes


def get_sentence_without_quotes(sentence, quote_end_indexes, quote_start_indexes):
    sentence_without_quotes = ""
    pairs = []

    print(quote_end_indexes, quote_start_indexes)

    print("pairs:", pairs)

    for pair in pairs:
        sentence_without_quotes += " " + \
            sentence.words[pair[0]:pair[1]].enclosing_text

    return sentence_without_quotes.strip()
