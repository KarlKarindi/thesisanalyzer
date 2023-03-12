from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .db import DB_USER, DB_PASS

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
app.run(host='0.0.0.0', port=5000)