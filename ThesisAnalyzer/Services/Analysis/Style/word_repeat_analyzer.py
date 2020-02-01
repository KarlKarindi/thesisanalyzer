from ThesisAnalyzer.Models.LemmaStopword import LemmaStopword
from ThesisAnalyzer.Models.Lemma import Lemma

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

    def get_scores_for_lemmas(lemmas_for_analysis, lemma_to_rank_and_count, user_word_count):
        """ Creates scores for lemmas """

        lemma_to_score = {}
        

        for lemma in lemmas_for_analysis:
            return True

    # ___________________________ #

    # Remove punctuation from the list of lemmas
    lemmas_without_punctuation = [
        lemma for lemma in Text(text).lemmas if lemma.isalpha()]
    user_word_count = len(lemmas_without_punctuation)

    # Filter out all lemmas that aren't included in the text more than once
    lemmas_repeating = find_repeating_lemmas(lemmas_without_punctuation)

    # Query the database for all lemmas that are known. Get list of model Lemma
    Lemma_list = Lemma.query.all()

    # Find lemmas that are viable for analysis from our list of repeating lemmas
    lemmas_for_analysis = find_lemmas_viable_for_analysis(
        Lemma_list, lemmas_repeating)

    # Create a dictionary of lemma -> (rank, count)
    lemma_to_rank_and_count = create_lemma_to_rank_and_count(Lemma_list)

    # Estimating the expected use of the word in every-day language from its ranking in the list
    get_scores_for_lemmas(lemmas_for_analysis,
                          lemma_to_rank_and_count, user_word_count)

    # print(lemmas_for_analysis)
    # print("LEMMA-2-COUNT")
    # for lemma in lemmas_for_analysis:
    #    print(lemma, lemma_to_rank_and_count[lemma])
    # Only analyze the lemmas that are known in the database.
