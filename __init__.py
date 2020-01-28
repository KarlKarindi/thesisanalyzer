from flask import Flask
from estnltk import Vabamorf
from program_utils import *
import csv

# Initialize vabamorf singleton
vabamorf = Vabamorf.instance()

# Create csv file for lemmas #
create_csv_file_for_lemmas(
    "C:\\Users\\Karl\\PythonProjects\\ThesisAnalyzer\\lemma_kahanevas.txt")


def create_app():
    from . import routes, services, model
    app = Flask(__name__)
    routes.init_app(app)
    print("App update/creation successful.\n\n\n")
    return app
