import os
from flask import Blueprint, request, render_template
from ThesisAnalyzer.Services import style_main, utils, general_main

template_dir = os.path.abspath('../templates')
mod = Blueprint('route', __name__, template_folder=template_dir)

# For user input
@mod.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["user_text"]
        result = style_main.analyze(text)
        return render_template('result.html', result=result)

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
