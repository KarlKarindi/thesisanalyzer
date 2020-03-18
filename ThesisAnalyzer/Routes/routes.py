import os
from flask import Blueprint, request, render_template
from ThesisAnalyzer.Services import style_main, utils, general_main
import jsonpickle

template_dir = os.path.abspath('../templates')
mod = Blueprint('route', __name__, template_folder=template_dir)

# For user input
@mod.route('/', methods=["GET", "POST"])
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

        return render_template('result.html', result=result, is_impersonal=is_impersonal,
                               sentences_with_pv=sentences_with_pv, pv_in_sentences=pv_in_sentences,
                               long_sentences=long_sentences)

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
