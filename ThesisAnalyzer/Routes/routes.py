from ThesisAnalyzer.Services import analysis_main, utils, user_form
from ThesisAnalyzer.Services import profiler
from flask import Blueprint, request, render_template
from pprint import pprint
import jsonpickle
import os

template_dir = os.path.abspath('../templates')
mod = Blueprint('route', __name__, template_folder=template_dir)

# For the user form
@mod.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["user_text"]

        analysis_result = jsonpickle.decode(
            analysis_main.analyze(text, user_form=True))

        data = user_form.format_data(text, analysis_result)

        html = render_template('result.html',
                               elapsed_time=data.elapsed_time,
                               sentence_count=data.sentence_count,
                               word_count=data.word_count,
                               sentences_with_pv=data.sentences_with_pv,
                               pv_in_sentences=data.pv_in_sentences,
                               long_sentences=data.long_sentences,
                               overused_words=data.overused_words,
                               highlighted_sentences=data.highlighted_sentences,
                               highlighted_clusters=data.highlighted_clusters,
                               poolt_tarind_sentences=data.poolt_tarind_sentences,
                               olema_kesksona_sentences=data.olema_kesksona_sentences,
                               maarus_saavas_sentences=data.maarus_saavas_sentences
                               )

        id = analysis_result["id"]
        if id is not None:  # Meaning that the analysis is in the database
            analysis_main.add_html_to_database(id, html)

        return html

    # If a GET request is made, show index.html
    return render_template("index.html")


@mod.route('/documentation/', methods=["GET"])
def documentation():
    return render_template("documentation.html")

# For Raimond's API
@mod.route('/analyze/', methods=['POST'])
def analyze_API():
    print()  # useful for testing
    text = utils.json_to_text(request)
    return analysis_main.analyze(text)
