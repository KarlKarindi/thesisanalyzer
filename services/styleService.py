import estnltk
import nltk
from estnltk import Text, EstWordTokenizer, ClauseSegmenter
from pprint import pprint
from .utils import *
from collections import defaultdict
import simplejson as json
from .. import vabamorf


def analyze_style(request):
    text = json_to_text(request)
    sentences = Text(text).sentence_texts

    # for sent in sentences:
    #   analyze_sentence_length_by_verb_count(sent)

    # print(get_most_frequent_lemmas())

    text = "Mees, keda seal kohtasime, oli tuttav ja teretas meid."
    for s in sentences:
        print(segment_clauses_in_sentence(s))
    

    # pprint(list(zip(segmented)))

    # segmented = segmenter.annotate_indices()

    # pprint(list(zip(segmented.words, segmented.clause_indices, segmented.clause_annotations)))

    return "TODO: make style"


def tag_words(analysis):
    """ Tag all the words in a sentence using vabamorf.

        Parameters:
            analysis (list): one analysed sentence

        Returns:
            list of tags
            list of tuplets (word, tag)
    """

    tags = []
    words = []
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


def segment_clauses_in_sentence(sentence):
    """ Segments the clauses (osalausestamine)
        Returns:
            dict with clauses
     """
    segmenter = ClauseSegmenter()

    # The sentence must be morphologically analyzed and then segmented.
    prepared = vabamorf.analyze(sentence)
    segmented = segmenter.mark_annotations(prepared)

    clauses = defaultdict(list)
    for w in segmented:
        clause_index = w["clause_index"]
        text = w["text"]
        clauses[clause_index].append(text)

    return clauses
