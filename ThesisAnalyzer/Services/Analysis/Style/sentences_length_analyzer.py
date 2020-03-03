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
            sentence.text, quote_analyzer)

        clauses_dict = segment_clauses_in_sentence(
            sentence, clause_segmenter, vc_detector)

        # sentence_is_long = is_sentence_too_long(
        #   clauses_dict, sentence)

        # if sentence_is_long:
        #   sentencesLengthSummary.add_sent_to_long_sentences(sentence)

    # Terminate the ClauseSegmenter process
    clause_segmenter.close()

    return sentencesLengthSummary


def add_word_info_layer_to_sentence(sentence, quote_analyzer):
    """ Adds a word_info layer to the sentence Text object.
        word_info layer contains attributes:
            word_id - index of the word in a sentence.
            in_quotes - whether the word is in quotes or not.
     """

    sentence = Text(sentence)
    sentence.tag_layer()

    word_info = Layer(name="word_info",
                      attributes=["word_id", "in_quotes"])
    sentence.add_layer(word_info)

    # Populate the layer
    for i, word in enumerate(sentence.words):
        word_text = word.text
        in_quot = quote_analyzer.is_word_in_quotes(word_text)
        word_info.add_annotation(word, word_id=i, in_quotes=in_quot)

    return sentence


def segment_clauses_in_sentence(sentence, clause_segmenter, vc_detector):
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

    # Create a dictionary of the clauses and the words they consist of
    clause_index_to_words = defaultdict(list)

    # pprint(clauses)

    word_id = 0
    for i, analysis in enumerate(clauses):
        # What about enclosing text?
        clause_text = analysis.text
        clause_type = analysis.clause_type
        clause_index_to_words[i] = clause_text

        # If a word is in quotes, don't add it into the clause, as it might be a title or quote.
        # if not in_quotes:
        #    clause_indexes_to_words[clause_index].append(word)
        # else:
        #   indexes_of_words_in_quotes.add(word_id)

    # pprint(clause_index_to_words)

    # Find verb chains
    # clauses_dict = map_clauses_to_verb_chains(
     #   sentence, clause_index_to_words, word_index, vc_detector)
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


def map_clauses_to_verb_chains(sentence, clause_index_to_words,
                               word_index, vc_detector):
    """ Finds verb chains in the clauses of a sentence.

        Parameters:
            sentence (String) - string text of sentence
            clause_indexes_to_words (dict) - dictionary of clause indexes in the
            sentence mapped to words (not in quotes)
            # TODO  - update
        Returns: dict with clauses and the corresponding verb chains in clauses
    """

    sentence.tag_layer(["words", "sentences", "morph_analysis", "clauses"])
    vc_detector.tag(sentence)
    verb_chains = sentence.verb_chains

    print(verb_chains)

    # Filtering. Leaves only the verb chains that aren't in quotes

    # clause_index_to_verb_chain = map_clause_index_to_verb_chain_text(sentence, vc_analysis)

    # pprint(clause_indexes_to_words)


def map_clause_index_to_vc_text(clause_indexes_to_words, vc_text):
    """ Parameters:
            # TODO: update
            sentence (String) - sentence in text form
            starts_ends - tuplet that has the clause_index, list of verb_chain_starts, list of verb_chain_ends
        Returns: dict that maps clause index to the verb chains (in text form)
    """

    clause_index_to_verb_chain = {}

    pprint(vc_text)

    for vc in vc_text:
        vc_indexes = set([n[0] for n in vc])
        for key, value in clause_indexes_to_words.items():
            indexes = set([n[0] for n in value])
            # print(vc_indexes, indexes)
            if vc_indexes.issubset(indexes):
                clause_index_to_verb_chain[key] = vc

    print()
    # print(clause_index_to_verb_chain)

    # Iterate through the list of tuplets, map clauses to their verb chains
    # for index, words in clause_indexes_to_words.items():

    return clause_index_to_verb_chain
