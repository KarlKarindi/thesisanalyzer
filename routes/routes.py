from flask import Blueprint, request
from ..services import general_service as service

mod = Blueprint('routes', __name__)


@mod.route('/')
def index():
    return "<h1>Karl Erik Karindi lõputöö analüsaator<h1>"


@mod.route('/general/', methods=['POST'])
def analyze_general():
    print()  # useful for testing
    return service.analyze_general(request)


@mod.route('/style/', methods=['POST'])
def analyze_style():
    print()  # useful for testing
    return service.analyze_style(request)
