from ThesisAnalyzer.Models.LemmaStopword import LemmaStopword
from ThesisAnalyzer.Models.Lemma import Lemma
from ThesisAnalyzer.Services.Analysis.Style.config import OVERUSED_MULTIPLIER
from pprint import pprint

from collections import defaultdict
from estnltk.wordnet import wn
from estnltk import Text
import math


class OverusedWordSummary(object):
    """ Container object for word usage analysis """

    def find_synonyms_for_words_and_lemma(self):
        """ Finds synonyms for the words and the lemma """
        # Create a list of synsets corresponding to the words
        w_syns = self.find_best_synonyms_for_words()
        w_syns_readable = w_syns
        w_syns[:] = [extract_word_from_Synset_object(
            word_syn) for word_syn in w_syns]

        # Create a list of synsets corresponding to the lemma
        # Remove duplicates by temporarily making the list into a set
        l_syns = wn.synsets(self.lemma)
        l_syns_readable = l_syns
        l_syns[:] = list(
            set([extract_word_from_Synset_object(lemma_syn) for lemma_syn in l_syns]))

        w_syns_final = remove_duplicate_synonyms_for_words(
            self.words, w_syns_readable)
        l_syns_final = remove_duplicate_synonyms_for_lemma(
            self.lemma, l_syns_readable)

        self.words_synonyms = w_syns_final
        self.lemma_synonyms = l_syns_final

    def find_best_synonyms_for_words(self):
        """ Finds the best synonyms for all the words """
        word_synonyms = []
        for word in self.words:
            word_synonyms.append(best_synset(word[0], word[1]))
        return word_synonyms

    # On initialization, don't find the synonyms.
    # Finding synonyms gets called out only on the top 20 most overused words
    def __init__(self, lemma, words_in_text, multiplier):
        self.multiplier = multiplier
        self.lemma = lemma
        self.words = [key for key in words_in_text]  # Convert set to list
        self.words_synonyms = []
        self.lemma_synonyms = []


def best_synset(word, pos):
    """ Finds the best synset for a word, takes into account part of speech """
    conversion = {"S": wn.NOUN, "V": wn.VERB, "A": wn.ADJ, "D": wn.ADV}

    if pos not in conversion:
        return None
    # What synsets contain this word (taking into account the part of speech)
    syns = wn.synsets(word, pos=conversion[pos])
    # If this word isn't in the wordnet, then return none
    if len(syns) == 0:
        return None
    # If there's only one synonym, return it
    if len(syns) == 1:
        return syns[0]
    # If there's more than one, return the one with the smallest number
    names = [s.name.split('.') for s in syns]
    best_name = names[0]
    for n in names:
        if n[0] == word and best_name[0] != word:
            best_name = n
        elif n[0] == word:
            if n[2] < best_name[2]:
                best_name = n
    return syns[names.index(best_name)]


def extract_word_from_Synset_object(synset):
    if synset is None:
        return None

    return str(synset).split("'")[1].split(".")[0]


def remove_duplicate_synonyms_for_lemma(lemma, syn_list):
    """ Convert synonyms that are the same as the lemma to None """
    result = []
    for syn in syn_list:
        if syn != lemma:
            result.append(syn)
    # If all the synonyms are None, return an empty list
    if result.count(None) == len(syn_list):
        return []
    return result


def remove_duplicate_synonyms_for_words(word_list, syn_list):
    """ Convert synonyms that are the same as the word to None """
    if len(word_list) != len(syn_list):
        return []

    result = []

    i = 0
    for word in word_list:
        if word[0] != syn_list[i]:
            result.append(syn_list[i])
        else:
            result.append(None)
        i += 1
    return result


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
                pos = analysis[0]["partofspeech"]
                lemma_to_word[lemma].add((word, pos))

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

        words_in_text = lemma_to_word[lemma]

        if multiplier > OVERUSED_MULTIPLIER:
            results.append(OverusedWordSummary(
                lemma, words_in_text, multiplier))

    # Sort the results list by multiplier (descending order). Only leave the 20 most overused words
    results = sorted(results, key=lambda x: x.multiplier, reverse=True)[:20]

    for overusedWordSummary in results:
        # Find the synonyms
        overusedWordSummary.find_synonyms_for_words_and_lemma()
        pretty_print_result(overusedWordSummary)

    print("Text word count:", user_word_count)
    return results


def pretty_print_result(overusedWordSummary):
    print("Lemma:", overusedWordSummary.lemma)
    print("Word:", overusedWordSummary.words)
    print("Multiplier:", overusedWordSummary.multiplier)
    print("Word synonyms:", overusedWordSummary.words_synonyms)
    print("Lemma synonym:", overusedWordSummary.lemma_synonyms)
    print()
