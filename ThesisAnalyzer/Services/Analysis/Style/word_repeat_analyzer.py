from ThesisAnalyzer.Models.LemmaStopword import LemmaStopword
from ThesisAnalyzer.Models.Lemma import Lemma

from estnltk import Text


def analyze_repeating_words(text):
    """ Analyzes repeating words using a method described in the Synonimity program """

    def find_repeating_lemmas(lemmas_all):
        """ Returns repeating lemmas from a list of all lemmas.
            Repeating lemmas do not include stopwords and must be alphabetical.
        """
        stop_words = [lemma_sw.name for lemma_sw in LemmaStopword.query.all()]
        return [lemma for lemma in lemmas_all if lemmas_all.count(lemma) > 1 and
                lemma not in stop_words and lemma.isalpha()]

    def find_lemmas_viable_for_analysis(lemmas_repeating):
        """ Finds the lemmas that are known in the database (viable for analysis).
            Returns the list of lemmas viable for analysis and the list of all known lemmas.
        """
        lemmas_viable = [lemma.lemma for lemma in Lemma.query.all()]
        return [lemma for lemma in lemmas_repeating if lemma in lemmas_viable]

    print("Length of text:", len(Text(text).lemmas))

    # Filter out the repeating lemmas. Only leave lemmas that are known in the database.
    lemmas = find_lemmas_viable_for_analysis(
        find_repeating_lemmas(Text(text).lemmas))

    # Only analyze the lemmas that are known in the database.
    print(len(lemmas))
