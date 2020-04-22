from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from ThesisAnalyzer.Services.cache import Cache
from db import DB_PASSWORD, DB_USER, DB_ADDRESS, DB_PORT, DB_NAME


# Globally accessible libraries
db = SQLAlchemy()
cache = Cache()


def create_app():
    import ThesisAnalyzer.Routes as Routes

    app = Flask(__name__)
    Routes.init_app(app)

    # Database initialization
    DB_URL = "postgresql://postgres:" + DB_PASSWORD + "@" + DB_ADDRESS + ":" + DB_PORT + "/" + DB_NAME

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    # silence the deprecation warning
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    print("App update/creation successful...\n\n\n")
    return app
