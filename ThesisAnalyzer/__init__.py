from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Globally accessible libraries
db = SQLAlchemy()


def create_app():
    import ThesisAnalyzer.Routes as Routes

    app = Flask(__name__)
    Routes.init_app(app)

    # Database initialization
    DB_URL = "postgresql://postgres:postgres@localhost:5432/analyzer"

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    # silence the deprecation warning
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    print("App update/creation successful...\n\n\n")
    return app
