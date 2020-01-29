from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from estnltk import Vabamorf
from program_utils import create_csv_file_for_lemmas

# Initialize vabamorf singleton
vabamorf = Vabamorf.instance()

POSTGRES_URL = ""
POSTGRES_USER = "postgres"
POSTGRES_PW = "mandariin"
POSTGRES_DB = "analyzer"

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
    user=POSTGRES_USER, pw=POSTGRES_PW, url=POSTGRES_URL, db=POSTGRES_DB)


# Create csv file for lemmas #
create_csv_file_for_lemmas(
    "C:\\Users\\Karl\\PythonProjects\\ThesisAnalyzer\\lemma_kahanevas.txt")


def create_app():
    from . import Routes, Models, Services
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)

    Routes.init_app(app)

    print("App update/creation successful.\n\n\n")
    return app
