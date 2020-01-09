from flask import Blueprint

style_bp = Blueprint('style_bp', __name__)

@style_bp.route('/style')
def style():
   print("I am on style route")
   return "style"