from flask import Blueprint, request
from ..services import style_service as service

mod = Blueprint('style', __name__)


