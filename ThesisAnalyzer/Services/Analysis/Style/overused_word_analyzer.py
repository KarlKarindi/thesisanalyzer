from ThesisAnalyzer.Models.LemmaStopword import LemmaStopword
from ThesisAnalyzer.Models.Lemma import Lemma
from ThesisAnalyzer.Services.Analysis.Style.config import OVERUSED_MULTIPLIER
from pprint import pprint

from collections import defaultdict
from estnltk import Text
import math


class OverusedWordAnalysis(object):

    def __init__(self, lemma, word, multiplier):
        self.lemma = lemma
        self.word = word
        self.multiplier = multiplier


def analyze_overused_words(text):
    """ Analyzes repeating words using a method described in the Synonimity program """

    def get_words_without_punctuation(text):
        return [word for word in Text(text).word_texts if word.isalpha()]

    def get_lemmas_without_punctuation(text):
        return [lemma for lemma in Text(text).lemmas if lemma.isalpha()]

    def map_lemma_to_word(text, words, lemmas):
        """ Returns: defaultdict that maps lemmas to their corresponding words """

        lemma_to_word = defaultdict(set)

        for word in words:
            analyses = Text(word).analysis
            for analysis in analyses:
                lemma = analysis[0]["lemma"]
                lemma_to_word[lemma].add(word)

        return lemma_to_word

    def find_repeating_lemmas(lemmas_all):
        """ Returns: repeating lemmas from a list of all lemmas.
            Repeating lemmas do not include stopwords and must be alphabetical.
            An overused lemma must be used in the text at least 3 times.
        """
        stop_words = [Lemma_sw.name for Lemma_sw in LemmaStopword.query.all()]
        return [lemma for lemma in lemmas_all if lemmas_all.count(lemma) > 2 and
                lemma not in stop_words and lemma.isalpha()]

    def find_lemmas_viable_for_analysis(Lemma_list, lemmas_repeating):
        """ Returns: list of lemmas that are viable for analysis (known in the database) """

        Lemma_name_list = [Lem.lemma for Lem in Lemma_list]
        return [lemma for lemma in lemmas_repeating if lemma in Lemma_name_list]

    def create_lemma_to_count_in_user_text(lemmas_for_analysis):
        """ Returns: dictionary of lemma to its count in the user text """

        lemma_to_count_in_user_text = {}
        for lemma in lemmas_for_analysis:
            if lemma not in lemma_to_count_in_user_text.keys():
                lemma_to_count_in_user_text[lemma] = 1
            else:
                lemma_to_count_in_user_text[lemma] += 1

        return lemma_to_count_in_user_text

    def create_lemma_to_rank_and_count(Lemma_list):
        """ Iterates over list of model Lemma.
            Sorts the list beforehand to get the rank of each word.
            Returns: dictionary where the keys are lemmas in the database
            and the values tuplets of (rank, count)
        """

        Lemma_list_sorted = sorted(
            Lemma_list, key=lambda x: x.count, reverse=True)

        lemma_to_rank_and_count = {}
        rank = 1
        for Lem in Lemma_list_sorted:
            lemma_to_rank_and_count[Lem.lemma] = (rank, Lem.count)
            rank += 1
        return lemma_to_rank_and_count

    def get_frequency_of_most_used_word(Lemma_list):
        """ Gets the occurence of the most used lemma in Estonian. """

        Lemma_list_sorted = sorted(
            Lemma_list, key=lambda x: x.count, reverse=True)

        most_used_count = Lemma_list_sorted[0].count
        total_count = 0
        for Lem in Lemma_list_sorted:
            total_count += Lem.count

        return round(most_used_count / total_count, 3)

    def get_lemma_expected_frequency(most_used_word_frequency, rank):
        return most_used_frequency / rank

    def get_lemma_actual_frequency(lemma_count, total_count):
        return lemma_count / total_count

    # ___________________________ #

    # Query the database for all lemmas that are known. Get list of model Lemma
    Lemma_list = Lemma.query.all()

    words_all_without_punctuation = get_words_without_punctuation(text)
    lemmas_all_without_punctuation = get_lemmas_without_punctuation(text)

    lemma_to_word = map_lemma_to_word(
        text, words_all_without_punctuation, lemmas_all_without_punctuation)

    user_word_count = len(words_all_without_punctuation)

    # First, filter out all lemmas that aren't included in the text more than once,
    # Then find all the lemmas that are viable for analysis
    lemmas_for_analysis = find_lemmas_viable_for_analysis(
        Lemma_list, find_repeating_lemmas(lemmas_all_without_punctuation))

    # Create dictionary to store repeating lemmas with their counts in the user text
    lemma_to_count_in_user_text = create_lemma_to_count_in_user_text(
        lemmas_for_analysis)

    # Create a dictionary of lemma -> (rank, count)
    lemma_to_rank_and_count = create_lemma_to_rank_and_count(Lemma_list)

    # Occurence of the most used lemma in Estonian
    most_used_frequency = get_frequency_of_most_used_word(Lemma_list)

    lemmas = set(lemmas_for_analysis)

    results = []
    # Get the expected frequency of a lemma and compare it to the actual frequency
    # If the actual frequency is a lot higher than the expected frequency, the word may be overused
    for lemma in lemmas:

        expected_freq = get_lemma_expected_frequency(most_used_frequency,
                                                     lemma_to_rank_and_count[lemma][0])
        actual_freq = get_lemma_actual_frequency(
            lemma_to_count_in_user_text[lemma], user_word_count)
        multiplier = math.floor(actual_freq / expected_freq)

        word = lemma_to_word[lemma]

        if multiplier > OVERUSED_MULTIPLIER:
            result = OverusedWordAnalysis(lemma, word, multiplier)
            results.append(result)

    # Print results
    results = sorted(results, key=lambda x: x.multiplier, reverse=True)
    for summary in results:
        pretty_print_result(summary)

    print("Text word count:", user_word_count)


def pretty_print_result(overused_w_analysis):
    print("Lemma:", overused_w_analysis.lemma)
    print("Word:", overused_w_analysis.word)
    print("Multiplier:", overused_w_analysis.multiplier)
    print("\n")
