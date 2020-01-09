from flask import Blueprint

mod = Blueprint('style', __name__)

@mod.route('/style')
def route_style():
   print("I am on style route")
   return "style"