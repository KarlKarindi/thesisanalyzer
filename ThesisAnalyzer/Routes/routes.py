from flask import Blueprint, request
from ThesisAnalyzer.Services import general_service, style_service

mod = Blueprint('route', __name__)


@mod.route('/')
def index():
    return "<h1>Karl Erik Karindi lõputöö analüsaator<h1>"


@mod.route('/general/', methods=['POST'])
def analyze_general():
    print()  # useful for testing
    return general_service.analyze(request)


@mod.route('/style/', methods=['POST'])
def analyze_style(): 
    print()  # useful for testing
    return style_service.analyze(request)
