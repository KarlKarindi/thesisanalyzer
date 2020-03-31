from ThesisAnalyzer.Models.Analysis import OfficialeseSummary, PooltTarindContainer
from ThesisAnalyzer.Services import utils
from estnltk.converters.CG3_exporter import export_CG3
from estnltk.taggers.syntax.visl_tagger import VISLCG3Pipeline
from estnltk.taggers import VislTagger, SyntaxDependencyRetagger
from env import vislcg_path

from estnltk import Text
from pprint import pprint
import jsonpickle
import os
import math


def analyze(original_text, text_obj, sentences_layer):
    officialese_summary = OfficialeseSummary()

    # Syntax analysis setup.
    text_obj.tag_layer(["morph_extended"])
    # Create a VISLCG pipeline. vislcg_path refers to the binary vislcg file, then tag the text.
    pipeline = VISLCG3Pipeline(vislcg_cmd=vislcg_path)
    visl_tagger = VislTagger(vislcg3_pipeline=pipeline)
    visl_tagger.tag(text_obj)

    sentences, words = utils.preprocess_text(original_text, sentences_layer)
    sentence_spans = sentences_layer[["start", "end"]]

    # pprint(text_obj.morph_analysis)

    # SyntaxDependencyRetagger("visl").retag(text_obj)

    # Poolt-tarind analysis
    officialese_summary.poolt_tarind_summary = analyze_poolt_tarind(original_text,
                                                                    sentence_spans, sentences_layer)

    #analyze_saav(sentence_spans, text_obj, None)

    return officialese_summary


def analyze_poolt_tarind(original_text, sentence_spans, sentences_layer):
    """ Analyzes whether there is poolt-tarind in the text.
        An example of poolt-tarind is the following:
            "Kiirabi poolt korraldatud esmaabikursus."
        In this case, the position of the poolt-tarind is going to be
        [0, 13] or "Kiirabi poolt" in the original text
        Returns:
            poolt_tarind_list (list) - a list of PooltTarindContainer objects.
    """

    poolt_tarind_list = []
    for s_i, sentence in enumerate(sentences_layer):
        positions = sentence.words[["start", "end"]]
        prev_word_is_in_genitiv = False

        # Iterate on the word level
        for w_i, morph_analysis in enumerate(sentence.morph_analysis):
            curr_root = morph_analysis.root[0]
            curr_form = morph_analysis.form[0]

            if curr_root == "poolt" and prev_word_is_in_genitiv:
                # i - 1 is always >= 0, as this condition is accessed on the second word at the earliest
                offender_position = [positions[w_i - 1]
                                     [0][0], positions[w_i][0][1]]
                sentence_position = [sentence_spans[s_i]
                                     [0], sentence_spans[s_i][1]]
                offender_text = original_text[offender_position[0]
                    :offender_position[1]]

                poolt_tarind_list.append(PooltTarindContainer(
                    offender_text, sentence.enclosing_text, sentence_position, offender_position))

            if curr_form == "sg g" or curr_form == "pl g":
                prev_word_is_in_genitiv = True
            else:
                prev_word_is_in_genitiv = False

    return poolt_tarind_list


def analyze_saav(sentence_spans, sentence, words):
    for n in sentence.visl:
        if '@ADVL' in n.deprel:
            # Since the parent_id is a string, it is casted to int
            # Also, indexing starts at 1, since SyntaxDependencyRetagger's first node is the root node.
            # The lemma is taken from the words list, as visl doesn't give an accurate lemma.
            try:
                parent_id = int(n.annotations[0].parent_span.id[0]) - 1
            except ValueError:
                parent_id = 0

            # print(words[parent_id])
