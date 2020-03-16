from ThesisAnalyzer import db


class LemmaStopword(db.Model):
    """ Model for a lemma stopword """

    __tablename__ = "lemma_stopword"
    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String,
                     unique=False)

    def __repr__(self):
        return '<Lemma_SW (name:{})'.format(self.name)
