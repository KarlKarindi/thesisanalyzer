from ThesisAnalyzer.Models.LemmaStopword import LemmaStopword
from ThesisAnalyzer.Models.Lemma import Lemma

from collections import defaultdict
from estnltk import Text


def analyze_repeating_words(text):
    """ Analyzes repeating words using a method described in the Synonimity program """

    def find_repeating_lemmas(lemmas_all):
        """ Returns: repeating lemmas from a list of all lemmas.
            Repeating lemmas do not include stopwords and must be alphabetical.
        """
        stop_words = [Lemma_sw.name for Lemma_sw in LemmaStopword.query.all()]
        return [lemma for lemma in lemmas_all if lemmas_all.count(lemma) > 1 and
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

    def get_occurence_of_most_used_word(Lemma_list):
        """ Gets the occurence of the most used lemma in Estonian. """

        Lemma_list_sorted = sorted(
            Lemma_list, key=lambda x: x.count, reverse=True)

        most_used_count = Lemma_list_sorted[0].count
        total_count = 0
        for Lem in Lemma_list_sorted:
            total_count += Lem.count

        return round(most_used_count / total_count, 3)

    def get_scores_for_lemmas(lemmas_for_analysis, lemma_to_rank_and_count, user_word_count, most_used_occurence):
        """ Creates scores for lemmas """

        analyzed_lemma_to_score = defaultdict()
        print(most_used_occurence)
        for lemma in lemmas_for_analysis:
            rank_of_lemma = lemma_to_rank_and_count[lemma][0]
            print(rank_of_lemma)
            score = int((most_used_occurence / rank_of_lemma) * 1000000)
            analyzed_lemma_to_score[lemma] = score

        return analyzed_lemma_to_score

    # ___________________________ #

    # Remove punctuation from the list of lemmas
    lemmas_all_without_punctuation = [
        lemma for lemma in Text(text).lemmas if lemma.isalpha()]
    user_word_count = len(lemmas_all_without_punctuation)

    # Filter out all lemmas that aren't included in the text more than once
    lemmas_repeating = find_repeating_lemmas(lemmas_all_without_punctuation)

    # Query the database for all lemmas that are known. Get list of model Lemma
    Lemma_list = Lemma.query.all()

    # Find lemmas that are viable for analysis from our list of repeating lemmas
    lemmas_for_analysis = find_lemmas_viable_for_analysis(
        Lemma_list, lemmas_repeating)

    # Create dictionary to store repeating lemmas with their counts in the user text
    lemma_to_count_in_user_text = create_lemma_to_count_in_user_text(
        lemmas_for_analysis)

    # Create a dictionary of lemma -> (rank, count)
    lemma_to_rank_and_count = create_lemma_to_rank_and_count(Lemma_list)

    # Occurence of the most used lemma in Estonian
    most_used_occurence = get_occurence_of_most_used_word(Lemma_list)

    # Estimating the expected use of the word in every-day language from its ranking in the list
    print(get_scores_for_lemmas(lemmas_for_analysis,
                                lemma_to_rank_and_count, user_word_count, most_used_occurence))
