from flask import Blueprint

gen_bp = Blueprint('gen_bp', __name__)

@gen_bp.route('/general')
def general():
   print("I am on general route")
   return "general"