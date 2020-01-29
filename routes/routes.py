from flask import Blueprint, request
from ..Services import general_service
from ..Services import style_service

mod = Blueprint('route', __name__)


@mod.route('/')
def index():
    return "<h1>Karl Erik Karindi lõputöö analüsaator<h1>"


@mod.route('/general/', methods=['POST'])
def analyze_general():
    print()  # useful for testing
    return general_service.analyze_general(request)


@mod.route('/style/', methods=['POST'])
def analyze_style():
    print()  # useful for testing
    return style_service.analyze_style(request)
