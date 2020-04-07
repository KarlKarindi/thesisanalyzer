from ThesisAnalyzer.Models.Analysis import OfficialeseSummary, NormalTextSliceContainer, ParentChildContainer
from ThesisAnalyzer.Services import utils, profiler
from ThesisAnalyzer.Constants import constants
from estnltk.taggers.syntax.visl_tagger import VISLCG3Pipeline
from estnltk.taggers import VislTagger, SyntaxDependencyRetagger, VabamorfAnalyzer
from estnltk.resolve_layer_dag import make_resolver
from env import get_vislcg3_path
from estnltk import Text
from pprint import pprint
import jsonpickle
import os
import math


def analyze(original_text, orig_text_obj, sentences_layer):
    officialese_summary = OfficialeseSummary()

    text_obj = orig_text_obj
    resolver = make_resolver(disambiguate=False, guess=True)
    del text_obj.morph_analysis
    text_obj.tag_layer(resolver=resolver)["morph_analysis"]
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
        try:
            visl_tagger.tag(sentence_text_obj)
            SyntaxDependencyRetagger("visl").retag(sentence_text_obj)
        # Sometimes the dependency retagger breaks for unknown reasons.
        # For example, if the user input a file path for some reason.
        # Skip the sentence in that case.
        except:
            continue

        # Leave only the words that correspond to this sentence
        sent_words = sentence_words[i]

        # Analyze olema kesksõna
        officialese_summary.olema_kesksona_summary.extend(
            analyze_olema_kesksona(original_text, sentence_text_obj, sent_words))

        # Analyze poolt-tarind
        officialese_summary.poolt_tarind_summary.extend(
            analyze_poolt_tarind(original_text, sentence_text_obj, sent_words))

        # Analyze määrus saavas käändes
        officialese_summary.maarus_saavas_summary.extend(
            analyze_maarus_saavas(sentence_text_obj, sent_words))

        # Analyze nominalisatsioon mine-vormis
        officialese_summary.nominalisatsioon_mine_vormis_summary.extend(
            analyze_nominalisatsioon_mine_vorm(sentence_text_obj, sent_words))

    return officialese_summary


def analyze_olema_kesksona(original_text, sentence, words):
    """ Analyzes olema kesksõna.
        Example (offending sentence -> what the sentence should be):
            "Pakkumine on kehtiv 6 kuud" -> "Pakkumine kehtib 6 kuud"
        Parameters:
            original_text (String) - The original text as a string
            sentence (Text) - Sentence that has had syntax analysis done to it
            words (list) - All the words that are included in the sentence as WordSummary objects
        Returns:
            offenders (list) - List of NormalTextSliceContainer objects
    """

    offenders = []
    for i, word_analysis in enumerate(sentence.visl):
        # Check if the word is a predicate (predikaat) and if it's a verb (V) or an adjective (A)
        # Nouns must be filtered out. Otherwise "See on suur arv" is an offender.
        if ("@PRD" in word_analysis.deprel) and \
                ("A" in sentence.visl[i]["partofspeech"] or "V" in sentence.visl[i]["partofspeech"]) and \
                (words[i]["text"].endswith("tav") or words[i]["text"].endswith("v")):

            # Since the parent_span.id is a string, it is cast to int
            # Also, indexing starts at 1, since SyntaxDependencyRetagger's first node is the root node.
            # The lemma is taken from the words list, as visl doesn't give an accurate lemma.
            try:
                parent_id = int(word_analysis.annotations[0].parent_span.id[0]) - 1
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

                offender = NormalTextSliceContainer(sentence.text, sentence_position,
                                                    text, position)
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
            offenders (list) - List of NormalTextSliceContainer objects
    """

    offenders = []
    prev_word_is_in_genitiv = False

    for i, morph_analysis in enumerate(sentence.morph_analysis):
        curr_root = morph_analysis.root[0]
        curr_form = morph_analysis.form[0]

        if curr_root == "poolt" and prev_word_is_in_genitiv:
            # i - 1 is always >= 0, as this condition is accessed on the second word at the earliest
            # Take the previous word as an offender as well. Example: "Tema poolt"
            position = [words[i - 1]["position"][0], words[i]["position"][1]]
            sentence_position = words[i]["sentence_position"]
            text = original_text[position[0]:position[1]]

            offenders.append(NormalTextSliceContainer(sentence.text, sentence_position, text, position))

        if curr_form == "sg g" or curr_form == "pl g":
            prev_word_is_in_genitiv = True
        else:
            prev_word_is_in_genitiv = False

    return offenders


def analyze_maarus_saavas(sentence, words):
    """ Analyzes whether there is a määrus in saavas käändes officialese error.
        Example (offending sentence -> what the sentence should be):
             "Arsti sooviks on teha head" -> "Arst soovib teha head"
        Parameters:
            sentence (Text) - Sentence that has had syntax analysis done to it
            words (list) - All the words that are included in the sentence as WordSummary objects.
        Returns:
            offenders (list) - List of ParentChildContainer objects
    """
    offenders = []
    for i, word_analysis in enumerate(sentence.visl):
        # Check if the word is an adverb (määrsõna) and if its case is tr
        if "@ADVL" in word_analysis.deprel and "tr" in word_analysis.case and \
                word_analysis.text.lower() not in constants.MAARUS_SAAVAS_EXCEPTIONS:
            # Since the parent_span.id is a string, it is cast to int
            # Also, indexing starts at 1, since SyntaxDependencyRetagger's first node is the root node.
            # The lemma is taken from the words list, as visl doesn't give an accurate lemma.
            try:
                parent_id = int(word_analysis.annotations[0].parent_span.id[0]) - 1
            except ValueError:
                continue
            except AttributeError:
                continue
            # words list gives the correct lemma
            if words[parent_id]["lemma"] == "olema":
                offender = create_parent_child_container_instance(sentence, words, i, parent_id)
                offenders.append(offender)

    return offenders


def analyze_nominalisatsioon_mine_vorm(sentence, words):
    """ Analyzes whether there is a nominalisatsioon in mine vorm officialese error.
        Example (offending sentence -> what the sentence should be):
            "Teostame kontrollimist" -> "Kontrollime"
        Parameters:
            sentence (Text) - Sentence that has had syntax analysis done to it
            words (list) - All the words that are included in the sentence as WordSummary objects.
        Returns:
            offenders (list) - List of ParentChildContainer objects
    """

    offenders = []
    for i, word_analysis in enumerate(sentence.visl):
        if words[i]["lemma"].endswith("mine"):
            try:
                parent_id = int(word_analysis.annotations[0].parent_span.id[0]) - 1
            except ValueError:
                continue
            except AttributeError:
                continue

            if words[parent_id]["lemma"] in constants.NOMINALISATSIOON_MINE_VORM_TRIGGERS:
                offender = create_parent_child_container_instance(sentence, words, i, parent_id)
                offenders.append(offender)

    return offenders


def create_parent_child_container_instance(sentence, words, child_id, parent_id):
    """ Helper function that creates a ParentChildContainer object from parent and child data
        Parameters:
            sentence (Text) - Sentence that has had syntax analysis done to it
            words (list) - words (list) - All the words that are included in the sentence as WordSummary objects
            child_id (int) - index of the child word
            parent_id (int) - index of the parent word
        Returns:
            A ParentChildContainer object
     """
    parent = words[parent_id]
    parent_position = [parent["position"][0],
                       parent["position"][1]]
    child_position = [words[child_id]["position"][0],
                      words[child_id]["position"][1]]
    parent_text = parent["text"]
    child_text = words[child_id]["text"]
    sentence_position = parent["sentence_position"]
    return ParentChildContainer(sentence.text, sentence_position,
                                parent_position, child_position, parent_text, child_text)
