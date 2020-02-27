from ThesisAnalyzer.Models.LemmaStopword import LemmaStopword
from ThesisAnalyzer.Models.Lemma import Lemma
from ThesisAnalyzer.Services.Analysis.Style.Config import config

from collections import defaultdict
from estnltk.wordnet import wn
from estnltk import Text
from flask import jsonify
from pprint import pprint
import jsonpickle
import math

# TODO: CLUSTER FUNCTIONS.


class TextSummmary(object):
    """ Container class for OverusedWordSummary object """

    def __init__(self, word_count, OverusedWords):
        # word_count does not include stopwords
        self.word_count = word_count
        self.OverusedWordSummary = OverusedWords

# TODO: FIX WORD SYNONYMS.


class OverusedWordSummary(object):
    """ Container object for word usage analysis """

    def find_synonyms_for_words_and_lemma(self):
        """ Finds synonyms for the words and the lemma """
        # Create a list of synsets corresponding to the words
        # w_syns = self.find_best_synonyms_for_words()
        # w_syns_readable = w_syns
        # w_syns[:] = [extract_word_from_Synset_object(
        #    word_syn) for word_syn in w_syns]

        # Create a list of synsets corresponding to the lemma
        # Remove duplicates by temporarily making the list into a set
        l_syns = wn.synsets(self.lemma)
        l_syns_readable = l_syns
        l_syns[:] = list(
            set([extract_word_from_Synset_object(lemma_syn) for lemma_syn in l_syns]))

        # w_syns_final = remove_duplicate_synonyms_for_words(
        #    self.words, w_syns_readable)
        l_syns_final = remove_duplicate_synonyms_for_lemma(
            self.lemma, l_syns_readable)

        # self.words_synonyms = w_syns_final
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
        self.times_used = len(self.words)
        self.words_synonyms = []
        self.lemma_synonyms = []


class Word(object):

    def __init__(self, text, pos, start, end):
        self.text = text
        self.pos = pos
        self.start = start
        self.end = end


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


def analyze(text):
    """ Analyzes repeating words using a method described in the Synonimity program
        Returns: TextSummary object
    """

    # Query the database for all lemmas that are known. Get list of model Lemma
    Lemma_list = Lemma.query.all()

    # TODO: FIND SENTENCES CONTAINING WORDS
    text = Text(text)
    sentences = get_sentences(text)
    words = get_words(text)
    lemmas = get_lemmas(text)

    lemma_to_word = map_lemma_to_word(words, lemmas)

    user_word_count = len(words)

    # First, filter out all lemmas that aren't included in the text more than once,
    # Then find all the lemmas that are viable for analysis
    lemmas_for_analysis = find_lemmas_viable_for_analysis(
        Lemma_list, find_repeating_lemmas(lemmas))

    # Create dictionary to store repeating lemmas with their counts in the user text
    lemma_to_count_in_user_text = create_lemma_to_count_in_user_text(
        lemmas_for_analysis)

    # Create a dictionary of lemma -> (rank, count)
    lemma_to_rank_and_count = create_lemma_to_rank_and_count(Lemma_list)

    # Occurence of the most used lemma in Estonian
    most_used_frequency = get_frequency_of_most_used_word(Lemma_list)

    lemmas = set(lemmas_for_analysis)

    overusedWordSummaryList = []
    # Get the expected frequency of a lemma and compare it to the actual frequency
    # If the actual frequency is a lot higher than the expected frequency, the word may be overused
    for lemma in lemmas:

        expected_freq = get_lemma_expected_frequency(most_used_frequency,
                                                     lemma_to_rank_and_count[lemma][0])
        actual_freq = get_lemma_actual_frequency(
            lemma_to_count_in_user_text[lemma], user_word_count)
        multiplier = math.floor(actual_freq / expected_freq)

        words_in_text = lemma_to_word[lemma]

        if multiplier > config.OVERUSED_MULTIPLIER:
            overusedWordSummaryList.append(OverusedWordSummary(
                lemma, words_in_text, multiplier))

    # Sort the results list by multiplier (descending order)
    # Only leave config.OUW_NUM_WORDS_TO_ANALYZE words for analysis
    overusedWordSummaryList = sorted(
        overusedWordSummaryList, key=lambda x: x.multiplier, reverse=True)[:config.OUW_NUM_WORDS_TO_ANALYZE]

    for overusedWordSummary in overusedWordSummaryList:
        # Find the synonyms
        overusedWordSummary.find_synonyms_for_words_and_lemma()

    # Return a textSummary object
    textSummary = TextSummmary(user_word_count, overusedWordSummaryList)
    return textSummary


def get_sentences(text):
    """ Returns: dictionary with tuplet of (start, end) as key and sentence text as value"""
    keys = text.sentence_spans
    values = text.sentence_texts

    return dict(zip(keys, values))


def get_words(text):
    # FIXME: Add punctuation
    # return [word for word in Text(text).word_texts if word.isalpha()]
    return [word for word in text.words]


def get_lemmas(text):
    # FIXME: Add punctuation.
    # return [lemma for lemma in Text(text).lemmas if lemma.isalpha()]
    return [lemma for lemma in text.lemmas]


def map_lemma_to_word(words, lemmas):
    """ Returns: defaultdict that maps lemmas to their corresponding words """

    lemma_to_word = defaultdict(set)

    for word in words:
        analyses = Text(word).analysis
        if len(analyses) > 1:
            pprint(analyses)
        for analysis in analyses:
            lemma = analysis[0]["lemma"]
            text = word["text"]
            pos = analysis[0]["partofspeech"]
            start = word["start"]
            end = word["end"]

            word_obj = Word(text, pos, start, end)
            lemma_to_word[lemma].add(
                (word_obj))

    return lemma_to_word


def find_repeating_lemmas(lemmas_all):
    """ Returns: repeating lemmas from a list of all lemmas.
        Repeating lemmas do not include stopwords and must be alphabetical.
        An overused lemma must be used in the text at least config.MAX_COUNT_OF_LEMMA times.
    """
    stop_words = [Lemma_sw.name for Lemma_sw in LemmaStopword.query.all()]
    return [lemma for lemma in lemmas_all if lemmas_all.count(lemma) > config.MAX_COUNT_OF_LEMMA and
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
    return most_used_word_frequency / rank


def get_lemma_actual_frequency(lemma_count, total_count):
    return lemma_count / total_count


def pretty_print_ouw_summary(overusedWordSummary):
    print("Multiplier:", overusedWordSummary.multiplier)
    print("Lemma:", overusedWordSummary.lemma)
    print("Lemma synonym:", overusedWordSummary.lemma_synonyms)
    print("Word:", overusedWordSummary.words)
    print("Word synonyms:", overusedWordSummary.words_synonyms)
    print()
