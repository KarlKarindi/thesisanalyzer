from ThesisAnalyzer import vabamorf
from ThesisAnalyzer.Services.Analysis.Style.Config import config
from ThesisAnalyzer.Models.Feedback import StyleFeedback
from ThesisAnalyzer.Services import utils

from estnltk import Text, ClauseSegmenter
from collections import defaultdict

import statistics


def analyze(text):
    """ Function to start the clause analysis """
    sentences = Text(text).sentence_texts

    segmenter = ClauseSegmenter()

    for sentence in sentences:
        clauses = segment_clauses_in_sentence(sentence, segmenter)
        clauses_feedback = analyze_clauses_in_sentence(
            clauses, sentence)
    return None


def analyze_clauses_in_sentence(clauses, sentence):
    """ Analyzes the clauses in a sentence.
        Looks at clause word length, sentence word length, clause amount,
        returns feedback accordingly.

        Parameters:
            clauses - dictionary with clauses
        Returns:
            feedback - StyleFeedback object
    """
    feedback = StyleFeedback()

    # pprint(sentence)
    # pprint(clauses)
    # Count all the words in clauses
    total_word_count = 0
    clause_lengths = []
    for clause in clauses.values():
        clause_word_count = len(clause)
        total_word_count += clause_word_count
        clause_lengths.append(clause_word_count)
        #print("CLAUSE_LEN", clause_word_count)

    mean_word_count_in_clauses = total_word_count / len(clauses)
    median_word_count_in_clauses = statistics.median(
        clause_lengths)

    #print("MEAN_WORD_COUNT_IN_CLAUSE", mean_word_count_in_clauses)
    #print("MEDIAN_WORD_COUNT_IN_CLAUSE", median_word_count_in_clauses)
    #print("WORD_COUNT", total_word_count)
    # print()

    # FIXME: Kui on loetelu, milles on nt pealkirjad vms, siis vaata, mida teha. Sama tsitaatidega.
    if len(clauses) > config.MAX_CLAUSE_AMOUNT:
        print('Lause\n"' + sentence +
              '"\ntundub liiga pikk. Võimalik, et seda saab lühemaks teha.')

    # Äkki on võimalik teha osalause võrdlust? Näiteks vaadata osalausete sõnaarvu mediaani
    # ning vaadata, kas mingi osalause erineb sellest väga palju.

    return feedback


def segment_clauses_in_sentence(sentence, segmenter):
    """ Segments the clauses (osalausestamine)

        Parameters:
            sentence - one sentence (as a string)
            segmenter - ClauseSegmenter
        Returns:
            dictionary with clauses
     """

    # TODO: Try Except

    # The sentence must be morphologically analyzed and then segmented.
    prepared = vabamorf.analyze(sentence)
    segmented = segmenter.mark_annotations(prepared)

    # Create a dictionary of the clauses and the words they consist of.
    clauses = defaultdict(list)
    in_quotes = False

    for word in segmented:
        word_text = word["text"]

        in_quotes = utils.is_word_in_quotes(word_text, in_quotes)
        print(word_text, in_quotes)

        if not in_quotes:
            clause_index = word["clause_index"]
            clauses[clause_index].append(word_text)

    return clauses
