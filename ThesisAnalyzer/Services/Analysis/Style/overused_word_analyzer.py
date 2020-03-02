from ThesisAnalyzer.Models.LemmaStopword import LemmaStopword
from ThesisAnalyzer.Models.Lemma import Lemma
from ThesisAnalyzer.Services.Analysis.Style.Config import config

from collections import defaultdict
#from estnltk.wordnet import wn
from estnltk import Text
from flask import jsonify
from pprint import pprint
import jsonpickle
import math


class TextSummmary(object):
    """ Container class for OverusedWordSummary object """

    def __init__(self, word_count, OverusedWords):
        # word_count does not include stopwords
        self.word_count = word_count
        self.OverusedWordSummary = OverusedWords

# TODO: FIX WORD SYNONYMS.


class OverusedWordSummary(object):
    """ Container object for word usage analysis """

    def find_synonyms_for_lemma(self):
        """ Finds synonyms for the lemma """

        # TODO: FIX FOR estnltk 1.6
        # Create a list of synsets corresponding to the lemma
        # Remove duplicates by temporarily making the list into a set
        #l_syns = wn.synsets(self.lemma)
        #l_syns_readable = l_syns
        # l_syns[:] = list(
        #    set([extract_word_from_Synset_object(lemma_syn) for lemma_syn in l_syns]))

        # l_syns_final = remove_duplicate_synonyms_for_lemma(
        #    self.lemma, l_syns_readable)

        #self.lemma_synonyms = l_syns_final

    def add_cluster(self, cluster):
        self.clusters.append(cluster)

    # On initialization, don't find the synonyms.
    # Finding synonyms gets called out only on the top 20 most overused words
    def __init__(self, lemma, words_in_text, multiplier):
        self.multiplier = multiplier
        self.lemma = lemma
        # Create a list from the set of words_in_text, then sort it by start index.
        words = [key for key in words_in_text]
        self.words = sorted(words, key=lambda x: x.start, reverse=False)
        self.times_used = len(self.words)
        self.words_synonyms = []
        self.lemma_synonyms = []
        self.clusters = []

    def __repr__(self):
        return self.lemma


class WordSummary(object):

    def __init__(self, text, pos, start, end):
        self.text = text
        self.pos = pos
        self.start = start
        self.end = end

    def __repr__(self):
        return '<Word (text: {}, start: {}, end: {})>'.format(self.text, self.start, self.end)


class SentencesContainer(object):

    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end


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


def analyze(original_text):
    """ Analyzes repeating words using a method described in the Synonimity program
        Returns: TextSummary object
    """

    # Query the database for all lemmas that are known. Get list of model Lemma
    Lemma_list = Lemma.query.all()

    text = Text(original_text)
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

    sentences = get_sentences(text)

    # Get the expected frequency of a lemma and compare it to the actual frequency
    # If the actual frequency is a lot higher than the expected frequency, the word may be overused
    overusedWordSummaryList = []
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
        overusedWordSummary.find_synonyms_for_lemma()

        Words = overusedWordSummary.words
        # Only leave clusters where the usage of a word is more than config.MAX_CLUSTER_SIZE
        # If a word is used less than MAX_CLUSTER_SIZE times, the cluster is empty
        clusters = find_large_clusters(dict(enumerate(create_clusters(Words))))

        if (len(clusters) > 0):
            sentences_in_clusters = find_sentences_in_clusters(
                sentences, clusters)

            results = format_text(original_text, sentences_in_clusters)
            overusedWordSummary.add_cluster(results)

    # Return a textSummary object
    textSummary = TextSummmary(user_word_count, overusedWordSummaryList)
    return textSummary


def get_sentences(text):
    """ Returns: dictionary with tuplet of (start, end) as key and
        dictionary of sentence with index, text, start and end keys.
    """
    keys = text.sentence_spans
    sentences = text.sentence_texts
    sentence_spans = text.sentence_spans
    values = []
    for i, sent in enumerate(sentences):
        values.append(
            ({"index": i, "text": sent, "start": sentence_spans[i][0], "end": sentence_spans[i][1]}))

    return dict(zip(keys, values))


def get_words(text):
    # FIXME: Add punctuation
    # return [word for word in Text(text).word_texts if word.isalpha()]
    return [word for word in text.words]


def get_lemmas(text):
    # FIXME: Add punctuation.
    # return [lemma for lemma in Text(text).lemmas if lemma.isalpha()]
    return [lemma for lemma in text.lemmas if lemma]


def map_lemma_to_word(words, lemmas):
    """ Returns: defaultdict that maps lemmas to their corresponding words.
        Words are of type WordSummary
    """

    lemma_to_word = defaultdict(set)

    for word in words:
        analyses = Text(word).analysis
        if len(analyses) > 1:
            # TODO: Wtf do I do when there are many analyses?
            print("word", word)
            print("LEN ANALYSIS > 1:", analyses)
            print()
        for analysis in analyses:
            lemma = analysis[0]["lemma"]
            text = word["text"]
            pos = analysis[0]["partofspeech"]
            start = word["start"]
            end = word["end"]

            word_obj = WordSummary(text, pos, start, end)
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
    """ Parameters: lemmas_for_analysis - list of lemmas
        Returns: dictionary of lemma to its count in the user text
    """

    lemma_to_count_in_user_text = {}
    for lemma in lemmas_for_analysis:
        lemma_to_count_in_user_text[lemma] = lemmas_for_analysis.count(lemma)

    return lemma_to_count_in_user_text


def create_lemma_to_rank_and_count(Lemma_list):
    """ Iterates over list of model Lemma.
        Sorts the list beforehand to get the rank of each word.

        Parameters: Lemma_list - list of objects Lemma
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
    """ Gets the frequency of the most used lemma in Estonian. """

    Lemma_list_sorted = sorted(
        Lemma_list, key=lambda x: x.count, reverse=True)

    most_used_count = Lemma_list_sorted[0].count
    total_count = 0
    # Must be iterated over to add to total_count, as Lemma_list is a list of Lemma objects
    for Lem in Lemma_list_sorted:
        total_count += Lem.count

    return round(most_used_count / total_count, 3)


def get_lemma_expected_frequency(most_used_word_frequency, rank):
    return most_used_word_frequency / rank


def get_lemma_actual_frequency(lemma_count, total_count):
    return lemma_count / total_count


def create_clusters(Words):
    """ Generator function that creates clusters of overused words.
        Searches for words that aren't further away from each-other than config.CLUSTER_DISTANCE
        Clustering function found here:
        https://stackoverflow.com/questions/15800895/finding-clusters-of-numbers-in-a-list
    """

    previous = None
    cluster = []
    for Word in Words:
        if not previous or Word.start - previous <= config.CLUSTER_DISTANCE:
            cluster.append(Word)
        else:
            yield cluster
            cluster = [Word]
        previous = Word.start
    if cluster:
        yield cluster


def find_large_clusters(clusters):
    """ Finds clusters that have a size larger than config.MAX_CLUSTER_SIZE
        Returns: list of large clusters. If a cluster isn't large enough, an empty list is returned.
    """
    large_clusters = []
    for key in clusters:
        if len(clusters[key]) > config.MAX_CLUSTER_SIZE:
            large_clusters.append(clusters[key])

    return large_clusters


def find_sentences_in_clusters(sentences, clusters):
    """ Finds all the sentences according to the clusters.
        Parameters: sentences - dict of all sentences with key (start, end) and values (index, sentence)
        Returns: list of values (index, sentence)
    """

    # Iterates through all the words in a cluster
    result = []
    for Word_list in clusters:

        sentences_in_cluster = []
        # In a cluster, finds the sentence that every word belongs to
        for Word in Word_list:
            sent = find_sentence_by_word(sentences, Word)
            if sent not in sentences_in_cluster:
                sentences_in_cluster.append(sent)
        result.append(sentences_in_cluster)

    return result


def find_sentence_by_word(sentences, Word):
    """ Finds the sentence that word (type WordSummary) belongs to.
        Parameters:
            sentences - dictionary of all sentences with key (start, end) and values (index, sentence)
            word - object of type WordSummary
    """
    # TODO: Error handling if sentence isn't found.

    for key in sentences.keys():
        if key[0] <= Word.start <= key[1]:
            return sentences[key]


def format_text(original_text, sentences_in_clusters):
    """ Formatting text for the SentencesContainer class.
        First, checks if all the sentences in a cluster are continuous.
        If the sentences are continuous, add a slice of the original text to the output.
        If the sentences aren't continuous, replace missing sentences with [...]

        Parameters:
            original_text (string) - the original thesis text as one string.
            sentences_in_clusters - for an overused word: a list of lists where
                                    each embedded list is a cluster of sentences.
        Returns: a list of SentencesContainer objects.
    """

    results = []
    for cluster in sentences_in_clusters:

        # Find the start and end indexes, as these are necessary anyway
        start = cluster[0]["start"]
        end = cluster[len(cluster) - 1]["end"]

        # Decide formatting style on whether all the sentences are connected or not
        if sentences_are_connected(cluster):
            text = original_text[start:end]
        else:
            # TODO: Check if everything works nicely
            # Initialize a string, start appending sentences to it
            text = ""
            for i in range(len(cluster)):
                # Check if sentences are connected to eachother
                if i + 2 <= len(cluster) and sentences_are_connected(cluster[i: i + 2]):
                    text += " " + cluster[i]["text"]
                else:
                    text += " " + cluster[i]["text"] + " [...] "
            # Remove whitespace and unnecessary symbols from the end of a text
            text = text.strip().strip("[...] ")

        result = SentencesContainer(text, start, end)
        results.append(result)

    return results


def sentences_are_connected(sentences_in_cluster):
    """ Checks whether sentences are connected.
        Sentences are connected when the indexes are right after each other.
        Returns (boolean) - whether sentences are connected or not.
    """
    connected = True

    prev = None
    for sent in sentences_in_cluster:
        current = sent["index"]
        if prev is not None and current - prev != 1:
            connected = False
        prev = current

    return connected


def pretty_print_ouw_summary(overusedWordSummary):
    print("Multiplier:", overusedWordSummary.multiplier)
    print("Lemma:", overusedWordSummary.lemma)
    print("Lemma synonym:", overusedWordSummary.lemma_synonyms)
    print("Word:", overusedWordSummary.words)
    print("Word synonyms:", overusedWordSummary.words_synonyms)
    print()
