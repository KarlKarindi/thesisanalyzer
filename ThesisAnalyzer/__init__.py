import logging
import nltk
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .db import DB_USER, DB_PASS

nltk.download('punkt')

DB_ADDRESS = "localhost"
DB_PORT = "5432"
DB_NAME = "analyzer"


db = SQLAlchemy()


import ThesisAnalyzer.Routes as Routes

app = Flask(__name__)
Routes.init_app(app)
db.init_app(app)

# Database initialization
DB_URL = "postgres://"+DB_USER+":"+DB_PASS+"@thesisanalyzer-db:5432/analyzer"
#DB_URL = "postgresql://postgres:" + DB_PASSWORD + "@" + "5432" + ":" + DB_PORT + "/" + DB_NAME

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
# silence the deprecation warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# configure logging
# Set up a file handler for Flask's default logger
file_handler = RotatingFileHandler('logs/flask.log', maxBytes=10000000, backupCount=3)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

# Set the log level to INFO for Flask's default logger
app.logger.setLevel(logging.INFO)

app.run(host='0.0.0.0', port=5000)