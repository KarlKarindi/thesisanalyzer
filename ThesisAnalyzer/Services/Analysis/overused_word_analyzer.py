from ThesisAnalyzer.Models.Lemma import Lemma, LemmaStopword
from ThesisAnalyzer.Config import analysis as config
from ThesisAnalyzer.Services import utils
from ThesisAnalyzer.Services.Analysis.TextAnalyzers.analyzers import QuoteAnalyzer
from ThesisAnalyzer.Models.Analysis import TextSummmary, OverusedWordSummary, WordSummary, ClusterContainer

from collections import defaultdict
from estnltk import Text
from flask import jsonify
from pprint import pprint
import jsonpickle
import math


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


def analyze(original_text, preprocessed_text, sentences_layer):
    """ Analyzes repeating words using a method described in the Synonimity program
        Returns: TextSummary object
    """

    # Query the database for all lemmas that are known. Get list of model Lemma
    Lemma_list = Lemma.query.all()

    # Get preprocessed info
    sentences = preprocessed_text.sentences
    words = preprocessed_text.words

    # Get the amount of sentences and words
    text_sentence_count = len(sentences)
    text_word_count = get_text_word_count(words)

    # Use the words list to map lemmas to the words the lemmas correspond to.
    quote_analyzer = QuoteAnalyzer()
    lemma_to_word = map_lemma_to_word(words, quote_analyzer)

    user_word_count = len(words)

    # First, filter out all lemmas that aren't included in the text more than once,
    # Then find all the lemmas that are viable for analysis
    repeating_lemmas = find_repeating_lemmas(
        lemma_to_word)
    lemmas_for_analysis = find_lemmas_viable_for_analysis(
        Lemma_list, repeating_lemmas)

    # Create a dictionary of Lemma -> (rank, count). Lemma list taken from the database.
    lemma_to_rank_and_count = create_database_lemma_to_rank_and_count(
        Lemma_list)

    # Create a set of lemmas that will be analysed.
    lemmas = set(lemmas_for_analysis)

    # Get the expected frequency of a lemma and compare it to the actual frequency
    # If the actual frequency is a lot higher than the expected frequency, the word may be overused
    overusedWordSummaryList = []

    for lemma in lemmas:

        expected_freq = get_lemma_expected_frequency_rating(lemma_to_rank_and_count[lemma][0])
        actual_freq = get_lemma_actual_frequency_rating(
            len(lemma_to_word[lemma]), user_word_count)

        multiplier = math.floor(actual_freq / expected_freq)

        words_in_text = lemma_to_word[lemma]

        if multiplier > config.OVERUSED_MULTIPLIER:
            ows = OverusedWordSummary(
                lemma, words_in_text, multiplier)
            overusedWordSummaryList.append(ows)

    # Sort the results list by multiplier (descending order)
    # Only leave config.OUW_NUM_WORDS_TO_ANALYZE words for analysis
    overusedWordSummaryList = sorted(
        overusedWordSummaryList, key=lambda x: x.multiplier, reverse=True)[:config.OUW_NUM_WORDS_TO_ANALYZE]

    for ows in overusedWordSummaryList:
        # Find the synonyms
        # overusedWordSummary.find_synonyms_for_lemma()

        # Iterate over all the words, assign an id to each word.
        # The id of a word corresponds to it's index in the words list.
        Words = ows.words
        for i, Word in enumerate(Words):
            Word.id = i

        # Only leave clusters where the usage of a word is more than config.MAX_CLUSTER_SIZE
        # If a word is used less than MAX_CLUSTER_SIZE times, the cluster is empty
        clusters = find_large_clusters(
            dict(enumerate(create_clusters_of_words(Words))))

        if (len(clusters) > 0):
            sentences_in_clusters = find_sentences_in_clusters(
                sentences, clusters)

            results = format_text(original_text, sentences_in_clusters)
            ows.add_cluster(results)

        # Add cluster information to words
        # The amount of nested for cycles is fine, as the cycles themselves are short
        for i, cluster in enumerate(ows.clusters):

            # Tag the cluster text to get the words and their positions.
            text = Text(cluster.text).tag_layer()
            # Creates an AttributeList. Contains lists of [start, end, text]
            cluster_word_position = text.words[["start", "end", "text"]]

            # Set the start index. Used when searching for the word position in a cluster
            start_index = 0

            # Iterate through each word
            for word in ows.words:
                # Check if a word belongs to a cluster or not
                if cluster.sentence_position[0] <= word.position[0] \
                        and word.position[1] <= cluster.sentence_position[1]:

                    # Add word id to cluster indexes and add cluster index to word
                    word.cluster_index = i
                    ows.clusters[i].word_indexes.append(word.id)

                    # Iterate through. start_index changes dynamically so that no word is analyzed twice
                    for j in range(start_index, len(cluster_word_position)):
                        # Necessary to take first element, as it's a list inside a list.
                        # curr_word in form [start, end, text]
                        curr_word = cluster_word_position[j][0]

                        if curr_word[2] == word.text:
                            # Word has been found from cluster. Update words cluster position
                            cluster_start = curr_word[0]
                            cluster_end = curr_word[1]
                            # Set start index to j + 1, so our next iteration continues after j
                            start_index = j + 1
                            break

                    # Add info about the cluster to a word
                    word.position_in_cluster = [cluster_start, cluster_end]

    # Return a textSummary object
    textSummary = TextSummmary(
        text_word_count, text_sentence_count, overusedWordSummaryList)
    return textSummary


def get_text_word_count(words):
    """ counts the number of words in a text.
        Words are alphabetical.
    """
    count = 0
    for w in words:
        if w["text"].isalpha():
            count += 1
    return count


def map_lemma_to_word(words, quote_analyzer):
    """ Maps all the words that are used to their respective lemmas.
        Only takes into account words not in quotes.
        Parameters:
            words (list) - list of words that in the format of get_words_in_sentence() output.
            Contains all the words in the text.
            quote_analyzer - instance of QuoteAnalyzer
        Returns:
            lemma_to_word (defaultdict) - WordSummary objects mapped to lemmas
        Return example:
            'olema': {word_summary_object_1, word_summary_object_2, ...}
    """

    lemma_to_word = defaultdict(set)
    # Iterate over all the words
    for i, word in enumerate(words):
        in_quotes = quote_analyzer.is_word_in_quotes(word["text"])
        if not in_quotes:
            word_obj = WordSummary(word["text"], word["pos"], [word["position"][0], word["position"][1]],
                                   word["sentence_index"], [word["sentence_position"][0], word["sentence_position"][1]])
            lemma_to_word[word["lemma"]].add(word_obj)

    return lemma_to_word


def find_repeating_lemmas(lemma_to_word):
    """ Returns: repeating lemmas from a list of all lemmas.
        Repeating lemmas do not include stopwords and must be alphabetical.
        An overused lemma must be used in the text at least config.MIN_COUNT_OF_LEMMA times.
    """
    stop_words = [Lemma_sw.name for Lemma_sw in LemmaStopword.query.all()]
    return [lemma for lemma in lemma_to_word.keys() if len(lemma_to_word[lemma]) >= config.MIN_COUNT_OF_LEMMA and
            lemma not in stop_words and lemma.isalpha()]


def find_lemmas_viable_for_analysis(Lemma_list, repeating_lemmas):
    """ Returns: list of lemmas that are viable for analysis (known in the database) """

    Lemma_name_list = [Lem.lemma for Lem in Lemma_list]
    return [lemma for lemma in repeating_lemmas if lemma in Lemma_name_list]


def create_database_lemma_to_rank_and_count(Lemma_list):
    """ Iterates over list of model Lemma. List taken from the database.
        Sorts (in descending order) the list beforehand to get the correct rank of each word.

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


def get_lemma_expected_frequency_rating(rank):
    """ We find the expected frequency by dividing 1 with the rank of our lemma """
    return 1 / rank


def get_lemma_actual_frequency_rating(lemma_count, total_count):
    return lemma_count / total_count


def create_clusters_of_words(Words):
    """ Generator function that creates clusters of overused words.
        Searches for words that aren't further away from each-other than config.CLUSTER_DISTANCE
        Clustering function found here:
        https://stackoverflow.com/questions/15800895/finding-clusters-of-numbers-in-a-list
    """

    previous = None
    cluster = []
    for Word in Words:
        if not previous or Word.position[0] - previous <= config.CLUSTER_DISTANCE:
            cluster.append(Word)
        else:
            yield cluster
            cluster = [Word]
        previous = Word.position[0]
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
        Parameters:
            sentences - dict of all sentences with key (start, end) and values (index, sentence)
            clusters (list) - list of lists. Each list is a cluster containing Words.
        Returns: list of values (index, sentence)
    """

    results = []
    # Iterates through all the words in a cluster
    for Word_list in clusters:

        sentences_in_cluster = []
        # In a cluster, finds the sentence that every word belongs to
        for Word in Word_list:
            sentence = find_sentence_by_word(sentences, Word)
            if sentence not in sentences_in_cluster:
                sentences_in_cluster.append(sentence)
        results.append(sentences_in_cluster)

    return results


def find_sentence_by_word(sentences, Word):
    """ Finds the sentence that word (type WordSummary) belongs to.
        Parameters:
            sentences - dictionary of all sentences with key (start, end)
            Word - object of type WordSummary
    """
    sentences_list = list(sentences)
    key = sentences_list[Word.sentence_index]
    return sentences[key]


def format_text(original_text, sentences_in_clusters):
    """ Formatting text for the ClusterContainer class.
        First, checks if all the sentences in a cluster are continuous.
        If the sentences are continuous, add a slice of the original text to the output.
        If the sentences aren't continuous, replace missing sentences with [...]

        Parameters:
            original_text (string) - the original thesis text as one string.
            sentences_in_clusters - for an overused word: a list of lists where
                                    each embedded list is a cluster of sentences.
        Returns: a list of ClusterContainer objects.
    """

    results = []
    for cluster in sentences_in_clusters:

        # Find the start and end indexes, as these are necessary anyway
        start = cluster[0]["position"][0]
        end = cluster[len(cluster) - 1]["position"][1]

        # Decide formatting style on whether all the sentences are connected or not
        if sentences_are_connected(cluster):
            text = original_text[start:end]
        else:
            # Initialize a string, start appending sentences to it
            text = ""
            for i in range(len(cluster)):

                curr_sentence = cluster[i]
                end_of_cluster = False
                try:
                    next_sentence = cluster[i + 1]
                except IndexError:
                    end_of_cluster = True

                # Check if sentences are connected to eachother
                if not end_of_cluster and sentences_are_connected([curr_sentence, next_sentence]):
                    text += " " + cluster[i]["text"]
                else:
                    text += " " + cluster[i]["text"] + " [...] "

            # Remove whitespace and unnecessary symbols from the end of a text
            text = text.strip().strip("[...] ")

        result = ClusterContainer(text, start, end)
        results.append(result)

    return results


def sentences_are_connected(sentences_in_cluster):
    """ Checks whether sentences are connected.
        Sentences are connected when the sentence indexes are right after each other.
        Returns (boolean) - whether sentences are connected or not.
    """
    connected = True

    previous_index = None
    for sentence in sentences_in_cluster:
        current_index = sentence["sentence_index"]
        if previous_index is not None and current_index - previous_index != 1:
            return False
        previous_index = current_index

    return connected
