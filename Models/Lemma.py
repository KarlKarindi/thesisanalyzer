from flask import current_app


class Lemma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    count = db.Column(db.Integer)

    def __repr__(self):
        return self.name + " (" + self.count+")"
