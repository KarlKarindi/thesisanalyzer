import estnltk
import nltk
import statistics
import simplejson as json

from flask import jsonify
from estnltk import Text, EstWordTokenizer, ClauseSegmenter
from pprint import pprint
from ThesisAnalyzer.Services.utils import *
from collections import defaultdict
from ThesisAnalyzer import vabamorf
from ThesisAnalyzer.Models.Feedback import StyleFeedback
from ThesisAnalyzer.Services.Config.StyleConfig import MAX_CLAUSE_AMOUNT

ADVERB = "D"


def analyze_style(request):

    feedback = StyleFeedback()

    text = json_to_text(request)
    sentences = Text(text).sentence_texts

    # Clause analysis
    for sentence in sentences:
        clauses = segment_clauses_in_sentence(sentence)
        clauses_feedback = analyze_clauses_in_sentence(clauses, sentence)

    # Tag analysis
    analyze_adverbs(sentences)

    return jsonify(length=feedback.length)


def analyze_adverbs(sentences):
    """ Tags all the sentences and finds the percentage of adverbs (määrsõnad) """

    adverb_count = 0
    total_count = 0
    tags = tag_words_in_sentences(sentences)

    for tag in tags:
        if tag == ADVERB:
            adverb_count += 1
        total_count += 1

    adverb_percentage = round((adverb_count / total_count) * 100, 2)
    print("Total count:", total_count)
    print("Adverb count:", adverb_count)
    print("Adverb percentage is", str(adverb_percentage)+"%")


def tag_words_in_sentences(sentences):
    """ Tag all the words in a list of sentences using vabamorf
        Parameters:
            sentences - List of sentences
        Returns:
            list of tags
    """

    tags = []
    for sentence in sentences:
        sentence_analysis = vabamorf.analyze(sentence)
        for word in sentence_analysis:
            tag = word["analysis"][0]["partofspeech"]
            tags.append(tag)

    return tags


def tag_words(analysis):
    """ Tag all the words in a sentence using vabamorf.
        Parameters:
            analysis (list): one analysed sentence
        Returns:
            list of tags
            list of tuplets (word, tag)
    """

    tags = []
    tags_with_words = []

    for analyzed_sent in analysis:
        tag = analyzed_sent["analysis"][0]["partofspeech"]
        word = analyzed_sent["text"]
        tags.append(tag)
        tags_with_words.append((word, tag))

    return tags, tags_with_words


def analyze_sentence_length_by_verb_count(sentence):
    """ Analyze the sentence by verb count.
        If there are too many verbs in a sentence,
        it can be considered to be too long.
    """

    analysis = vabamorf.analyze(sentence)
    tags, tags_with_words = tag_words(analysis)

    verb_count = 0
    for i in range(len(tags)):
        if tags[i] == "V":
            verb_count += 1
            print(analysis[i]["text"])

    return True


def analyze_clauses_in_sentence(clauses, sentence):
    """ Analyzes the clauses in a sentence.
        Looks at clause word length, sentence word length, clause number,
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
    median_word_count_in_clauses = statistics.mean(clause_lengths)

    #print("MEAN_WORD_COUNT_IN_CLAUSE", mean_word_count_in_clauses)
    #print("MEDIAN_WORD_COUNT_IN_CLAUSE", median_word_count_in_clauses)
    #print("WORD_COUNT", total_word_count)
    # print()

    if len(clauses) > MAX_CLAUSE_AMOUNT:
        feedback.length += 'Lause "'+sentence +\
            '" tundub liiga pikk. Võimalik, et seda saab lühemaks teha.\n'

    # Äkki on võimalik teha osalause võrdlust? Näiteks vaadata osalausete sõnaarvu mediaani
    # ning vaadata, kas mingi osalause erineb sellest väga palju.

    return feedback


def segment_clauses_in_sentence(sentence):
    """ Segments the clauses (osalausestamine)

        Parameters:
            sentence - one sentence (as a string)
        Returns:
            dictionary with clauses
     """
    segmenter = ClauseSegmenter()

    # The sentence must be morphologically analyzed and then segmented.
    prepared = vabamorf.analyze(sentence)
    segmented = segmenter.mark_annotations(prepared)

    # Create a dictionary of the clauses and the words they consist of.
    clauses = defaultdict(list)
    for word in segmented:
        clause_index = word["clause_index"]
        text = word["text"]
        clauses[clause_index].append(text)

    return clauses
