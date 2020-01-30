from flask_sqlalchemy import SQLAlchemy
from ThesisAnalyzer import db


class Lemma(db.Model):
    """ Model for lemma """

    __tablename__ = "lemma"
    id = db.Column(db.Integer,
                   primary_key=True)
    lemma = db.Column(db.String(200),
                      unique=False)
    count = db.Column(db.Integer,
                      unique=False)

    def __repr__(self):
        return '<Lemma ({}, {})>'.format(self.lemma, self.count)
