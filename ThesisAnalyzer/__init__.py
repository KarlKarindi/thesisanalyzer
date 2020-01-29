from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from estnltk import Vabamorf
from ThesisAnalyzer import Services
import os

# Initialize vabamorf singleton
vabamorf = Vabamorf.instance()


def create_app():
    import ThesisAnalyzer.Models

    app = Flask(__name__)

    print("CREATING APP")

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    Routes.init_app(app)

    print("App update/creation successful.\n\n\n")
    return app
