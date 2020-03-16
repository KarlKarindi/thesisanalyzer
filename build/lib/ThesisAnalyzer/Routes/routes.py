from flask import Blueprint, request
#from ThesisAnalyzer.Services import style_main
from ThesisAnalyzer.Services import general_main

mod = Blueprint('route', __name__)


@mod.route('/')
def index():
    return "<h1>Karl Erik Karindi lõputöö analüsaator<h1>"


@mod.route('/general/', methods=['POST'])
def analyze_general():
    print()  # useful for testing
    return general_main.analyze(request)


#@mod.route('/style/', methods=['POST'])
#def analyze_style():
#    print()  # useful for testing
#    return style_main.analyze(request)
