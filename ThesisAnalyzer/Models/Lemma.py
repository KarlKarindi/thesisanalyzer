from flask_sqlalchemy import SQLAlchemy
from ThesisAnalyzer import db


class Lemma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lemma_name = db.Column(db.String(200), unique=False)
    lemma_count = db.Column(db.Integer, unique=False)
