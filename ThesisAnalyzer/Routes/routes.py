import os
from flask import Blueprint, request, render_template
from ThesisAnalyzer.Services import style_main, utils, general_main
import jsonpickle
from pprint import pprint
from ThesisAnalyzer.Services import profiler

template_dir = os.path.abspath('../templates')
mod = Blueprint('route', __name__, template_folder=template_dir)

# For user input
@mod.route('/', methods=["GET", "POST"])
@profiler.profile
def index():
    if request.method == "POST":
        text = request.form["user_text"]
        general_result = jsonpickle.decode(general_main.analyze(text))
        result = jsonpickle.decode(style_main.analyze(text))

        is_impersonal = general_result["is_impersonal"]
        sentences_with_pv = general_result["sentences_with_pv"]
        pv_in_sentences = []

        for key in sentences_with_pv.keys():
            words = ", ".join(sentences_with_pv[key])
            pv_in_sentences.append(words)

        long_sentences = result["sentences_length_summary"]["long_sentences"]
        overused_words = result["text_summary"]["overused_word_summary"]

        # Create a list of sentences. Word summary is shortened here to WS.
        # Each highlighted sentence index corresponds to one word's summary. Has all the sentences of that word summary
        all_WS_sentences = []
        for word_summary in overused_words:
            one_WS_sentences = []  # Contains all the sentences of one word summary

            # Iterate over all the words for an overused word. Find the sentences the word is contained in.
            for word in word_summary["words"]:
                sentence_pos = word["sentence_position"]
                word_pos = word["position"]

                # Creates a list with 3 elements. Adds them to sentences list.
                sentence_before_word = text[sentence_pos[0]:word_pos[0]]
                word_in_bold = text[word_pos[0]:word_pos[1]]
                sentence_after_word = text[word_pos[1]:sentence_pos[1]]
                one_WS_sentences.append(
                    [sentence_before_word, word_in_bold, sentence_after_word])

            # Add all the sentences of one word summary to highlighted_sentences list.
            all_WS_sentences.append(one_WS_sentences)

        all_WS_clusters = []
        for word_summary in overused_words:
            one_WS_clusters = []
            words = word_summary["words"]

            for cluster in word_summary["clusters"]:
                sentence = []
                cluster_text = cluster["text"]
                word_indexes = cluster["word_indexes"]
                last_word_pos = 0
                for i in word_indexes:
                    word = words[i]
                    positions = word["position_in_cluster"]
                    before = cluster_text[last_word_pos:positions[0]]
                    bold = cluster_text[positions[0]:positions[1]]
                    sentence.append(before)
                    sentence.append(bold)
                    # Update the position of the last word's end.
                    last_word_pos = positions[1]
                # Add the remainder of the sentence.
                sentence.append(cluster_text[last_word_pos:])

                one_WS_clusters.append(sentence)
            all_WS_clusters.append(one_WS_clusters)

        return render_template('result.html', result=result, is_impersonal=is_impersonal,
                               sentences_with_pv=sentences_with_pv, pv_in_sentences=pv_in_sentences,
                               long_sentences=long_sentences, overused_words=overused_words,
                               highlighted_sentences=all_WS_sentences, highlighted_clusters=all_WS_clusters)

    return render_template("index.html")


@mod.route('/documentation/', methods=["GET"])
def documentation():

    return render_template("documentation.html")

# For Raimond's API
@mod.route('/general/', methods=['POST'])
def analyze_general():
    print()  # useful for testing
    text = utils.json_to_text(request)
    return general_main.analyze(text)


@mod.route('/style/', methods=['POST'])
def analyze_style():
    print()  # useful for testing
    text = utils.json_to_text(request)
    return style_main.analyze(text)
