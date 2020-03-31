from ThesisAnalyzer.Models.Analysis import OfficialeseSummary, PooltTarindContainer, MaarusSaavasContainer
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
    # Create a VISLCG pipeline. vislcg_path refers to the binary vislcg file.
    pipeline = VISLCG3Pipeline(vislcg_cmd=vislcg_path)
    visl_tagger = VislTagger(vislcg3_pipeline=pipeline)

    sentences, words = utils.preprocess_text(original_text, sentences_layer)

    # Tag the syntax for each sentence, then run analyses on the sentence.
    # The loop is necessary, as the SyntaxDependencyRetagger can only take one sentence at a time.
    for i, sentence in enumerate(sentences_layer):
        sentence_text_obj = Text(sentence.enclosing_text)
        sentence_text_obj.tag_layer(["morph_extended"])
        visl_tagger.tag(sentence_text_obj)
        SyntaxDependencyRetagger("visl").retag(sentence_text_obj)

        # Analyze määrust saavas käändes
        officialese_summary.maarus_saavas_summary.extend(
            analyze_maarus_saavas(sentence_text_obj, i, words))

    # Poolt-tarind analysis
    sentence_spans = sentences_layer[["start", "end"]]
    officialese_summary.poolt_tarind_summary = analyze_poolt_tarind(original_text,
                                                                    sentence_spans, sentences_layer)

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

                offender_text = original_text[offender_position[0]:
                                              offender_position[1]]

                poolt_tarind_list.append(PooltTarindContainer(
                    offender_text, sentence.enclosing_text, sentence_position, offender_position))

            if curr_form == "sg g" or curr_form == "pl g":
                prev_word_is_in_genitiv = True
            else:
                prev_word_is_in_genitiv = False

    return poolt_tarind_list


def analyze_maarus_saavas(sentence, sentence_index, all_words_list):
    """ Analyzes whether there is a määrus in saavas käändes officialese error.
        Example (offending sentence -> what the sentence should be):
             "Arsti sooviks on teha head" -> "Arst soovib teha head"
        Parameters:
            sentence (Text) - Sentence that has had syntax analysis done to it
            sentence_index (int) - index of the sentence
            all_words_list (list) - list of all the words in the original_text
        Returns:
            offenders (list) - List of MaarusSaavasContainer objects
    """

    # Only leave the words in the corresponding sentence
    words = [word for word in all_words_list if
             word["sentence_index"] == sentence_index]

    offenders = []
    for i, word in enumerate(sentence.visl):
        # Check if the word is an adverb (määrsõna) and if it's conditional (tingiv kõneviis)
        if '@ADVL' in word.deprel and 'tr' in word.case:
            # Since the parent_span.id is a string, it is cast to int
            # Also, indexing starts at 1, since SyntaxDependencyRetagger's first node is the root node.
            # The lemma is taken from the words list, as visl doesn't give an accurate lemma.
            try:
                parent_id = int(word.annotations[0].parent_span.id[0]) - 1
            except ValueError:
                continue
            if words[parent_id]["lemma"] == "olema":
                parent = words[parent_id]
                parent_position = [parent["position"][0],
                                   parent["position"][1]]
                child_position = [words[i]["position"][0],
                                  words[i]["position"][1]]
                parent_text = parent["text"]
                child_text = words[i]["text"]
                sentence_position = parent["sentence_position"]

                offender = MaarusSaavasContainer(sentence.text, sentence_position,
                                                 parent_position, child_position, parent_text, child_text)
                offenders.append(offender)

    return offenders
