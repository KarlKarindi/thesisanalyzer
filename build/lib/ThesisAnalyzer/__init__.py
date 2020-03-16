from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from estnltk import Vabamorf

# Globally accessible libraries

db = SQLAlchemy()

# Initialize vabamorf singleton
# vabamorf = Vabamorf.instance()


def create_app():
    import ThesisAnalyzer.Routes as Routes

    print("In_create_app before app")
    app = Flask(__name__)
    Routes.init_app(app)
    print("After")

    # Database initialization
    DB_URL = "postgresql://postgres:postgres@localhost:5432/analyzer"

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    # silence the deprecation warning
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    print("App update/creation successful...\n\n\n")
    return app