from flask import Blueprint, request
from ..services import styleService as service

mod = Blueprint('style', __name__)


@mod.route('/style/', methods=['POST'])
def analyze_style():
    print()  # useful for testing
    return service.analyze_style(request)
