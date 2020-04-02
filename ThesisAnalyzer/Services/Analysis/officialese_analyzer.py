from ThesisAnalyzer.Models.Analysis import OfficialeseSummary, PooltTarindContainer, \
    MaarusSaavasContainer, OlemaKesksonaContainer
from ThesisAnalyzer.Services import utils, profiler
from ThesisAnalyzer.Constants import constants
from estnltk.taggers.syntax.visl_tagger import VISLCG3Pipeline
from estnltk.taggers import VislTagger, SyntaxDependencyRetagger
from vislcg3 import get_vislcg3_path

from estnltk import Text
from pprint import pprint
import jsonpickle
import os
import math


def analyze(original_text, text_obj, sentences_layer):
    officialese_summary = OfficialeseSummary()

    # Syntax analysis setup.
    # Create a VISLCG pipeline. vislcg_path refers to the binary vislcg file.
    pipeline = VISLCG3Pipeline(vislcg_cmd=get_vislcg3_path())
    visl_tagger = VislTagger(vislcg3_pipeline=pipeline)

    sentences, words, sentence_words = utils.preprocess_text(
        original_text, sentences_layer)

    # Tag the syntax for each sentence, then run analyses on the sentence.
    # The loop is necessary, as the SyntaxDependencyRetagger can only take one sentence at a time.
    for i, sentence in enumerate(sentences_layer):
        sentence_text_obj = Text(sentence.enclosing_text)
        sentence_text_obj.tag_layer(["morph_extended"])
        visl_tagger.tag(sentence_text_obj)
        try:
            SyntaxDependencyRetagger("visl").retag(sentence_text_obj)
        # Sometimes the dependency retagger breaks. For example, if it starts to analyse a file path (user_input)
        # Skip the sentence in that case.
        except AssertionError:
            continue

        # Leave only the words that correspond to this sentence
        sent_words = sentence_words[i]

        # Analyze määrus saavas käändes
        officialese_summary.maarus_saavas_summary.extend(
            analyze_maarus_saavas(sentence_text_obj, sent_words))

        # Analyze olema kesksõna
        officialese_summary.olema_kesksona_summary.extend(
            analyze_olema_kesksona(original_text, sentence_text_obj, sent_words))

        # Analyze poolt-tarind
        officialese_summary.poolt_tarind_summary.extend(
            analyze_poolt_tarind(original_text, sentence_text_obj, sent_words))

    return officialese_summary


def analyze_maarus_saavas(sentence, words):
    """ Analyzes whether there is a määrus in saavas käändes officialese error.
        Example (offending sentence -> what the sentence should be):
             "Arsti sooviks on teha head" -> "Arst soovib teha head"
        Parameters:
            sentence (Text) - Sentence that has had syntax analysis done to it
            words (list) - All the words that are included in the sentence as WordSummary objects
        Returns:
            offenders (list) - List of MaarusSaavasContainer objects
    """
    offenders = []
    for i, word in enumerate(sentence.visl):
        # Check if the word is an adverb (määrsõna) and if it's conditional (tingiv kõneviis)
        if "@ADVL" in word.deprel and "tr" in word.case and word.text.lower() not in constants.MAARUS_SAAVAS_EXCEPTIONS:
            # Since the parent_span.id is a string, it is cast to int
            # Also, indexing starts at 1, since SyntaxDependencyRetagger's first node is the root node.
            # The lemma is taken from the words list, as visl doesn't give an accurate lemma.
            try:
                parent_id = int(word.annotations[0].parent_span.id[0]) - 1
            except ValueError:
                continue
            except AttributeError:
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


def analyze_olema_kesksona(original_text, sentence, words):
    """ Analyzes olema kesksõna.
        Example (offending sentence -> what the sentence should be):
            "Pakkumine on kehtiv 6 kuud" -> "Pakkumine kehtib 6 kuud"
        Parameters:
            original_text (String) - The original text as a string
            sentence (Text) - Sentence that has had syntax analysis done to it
            words (list) - All the words that are included in the sentence as WordSummary objects
        Returns:
            offenders (list) - List of OlemaKesksonaContainer objects
    """

    offenders = []
    for i, word in enumerate(sentence.visl):
        # Check if the word is a predicate (predikaat) and if it's a verb (V) or an adjective (A)
        # Nouns must be filtered out. Otherwise "See on suur arv" is an offender.
        if ("@PRD" in word.deprel) and \
                ("A" in sentence.visl[i]["partofspeech"] or "V" in sentence.visl[i]["partofspeech"]) and \
                (words[i]["text"].endswith("tav") or words[i]["text"].endswith("v")):

            # Since the parent_span.id is a string, it is cast to int
            # Also, indexing starts at 1, since SyntaxDependencyRetagger's first node is the root node.
            # The lemma is taken from the words list, as visl doesn't give an accurate lemma.
            try:
                parent_id = int(word.annotations[0].parent_span.id[0]) - 1
            except ValueError:
                continue
            except AttributeError:
                continue
            if words[parent_id]["lemma"] == "olema":
                parent = words[parent_id]
                sentence_position = parent["sentence_position"]
                parent_start, parent_end = parent["position"][0], parent["position"][1]
                child_start, child_end = words[i]["position"][0], words[i]["position"][1]
                position = [min(parent_start, child_start),
                            max(parent_end, child_end)]
                text = original_text[position[0]:position[1]]

                offender = OlemaKesksonaContainer(sentence.text, sentence_position,
                                                  position, text)
                offenders.append(offender)

    return offenders


def analyze_poolt_tarind(original_text, sentence, words):
    """ Analyzes whether there is poolt-tarind in the text.
        An example of poolt-tarind is the following:
            "Kiirabi poolt korraldatud esmaabikursus."
        In this case, the position of the poolt-tarind is going to be
        [0, 13] or "Kiirabi poolt" in the original text
        Parameters:
            original_text (String) - The original text as a string
            sentence (Text) - Sentence that has had syntax analysis done to it
            words (list) - All the words that are included in the sentence as WordSummary objects
        Returns:
            offenders (list) - List of PooltTarindContainer objects
    """

    offenders = []
    prev_word_is_in_genitiv = False

    # Iterate on the word level
    for i, morph_analysis in enumerate(sentence.morph_analysis):
        curr_root = morph_analysis.root[0]
        curr_form = morph_analysis.form[0]

        if curr_root == "poolt" and prev_word_is_in_genitiv:
            # i - 1 is always >= 0, as this condition is accessed on the second word at the earliest
            # Take the previous word as an offender as well. Example: "Tema poolt"
            offender_position = [words[i - 1]["position"][0], words[i]["position"][1]]
            sentence_position = words[i]["sentence_position"]
            offender_text = original_text[offender_position[0]:
                                          offender_position[1]]

            offenders.append(PooltTarindContainer(
                offender_text, sentence.text, sentence_position, offender_position))

        if curr_form == "sg g" or curr_form == "pl g":
            prev_word_is_in_genitiv = True
        else:
            prev_word_is_in_genitiv = False

    return offenders
