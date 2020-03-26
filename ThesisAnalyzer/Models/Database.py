from ThesisAnalyzer import db


class Formrequest(db.Model):

    __tablename__ = "formrequest"
    id = db.Column(db.Integer,
                   primary_key=True)
    timestamp = db.Column(db.DateTime)
    successful = db.Column(db.Boolean)
    result = db.Column(db.String)

    def __init__(self, timestamp, successful=False):
        self.timestamp = timestamp
        self.successful = successful


class LongSentence(db.Model):

    __tablename__ = "long_sentence"
    id = db.Column(db.Integer,
                   primary_key=True)
    formrequest = db.Column(db.Integer, db.ForeignKey(
        'formrequest.id'), nullable=False)
    text = db.Column(db.String())

    def __init__(self, formrequest, text):
        self.formrequest = formrequest
        self.text = text


class TextStatistics(db.Model):

    __tablename__ = "text_statistics"
    id = db.Column(db.Integer,
                   primary_key=True)
    formrequest = db.Column(db.Integer, db.ForeignKey(
        'formrequest.id'), nullable=False)
    sentence_count = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    adverb_count = db.Column(db.Integer)
    pronoun_count = db.Column(db.Integer)

    def __init__(self, formrequest, sentence_count, word_count, adverb_count, pronoun_count):
        self.formrequest = formrequest
        self.sentence_count = sentence_count
        self.word_count = word_count
        self.adverb_count = adverb_count
        self.pronoun_count = pronoun_count


class PersonalSentence(db.Model):

    __tablename__ = "personal_sentence"

    id = db.Column(db.Integer,
                   primary_key=True)
    formrequest = db.Column(db.Integer, db.ForeignKey(
        'formrequest.id'), nullable=False)
    sentence = db.Column(db.String())

    def __init__(self, formrequest, sentence):
        self.formrequest = formrequest
        self.sentence = sentence


class OverusedWord(db.Model):

    __tablename__ = "overused_word"

    id = db.Column(db.Integer,
                   primary_key=True)
    formrequest = db.Column(db.Integer, db.ForeignKey(
        'formrequest.id'), nullable=False)
    lemma = db.Column(db.String())
    times_used = db.Column(db.Integer)

    def __init__(self, formrequest, lemma, times_used):
        self.formrequest = formrequest
        self.lemma = lemma
        self.times_used = times_used


class ClusterOverusedWord(db.Model):

    __tablename__ = "cluster_overused_word"
    id = db.Column(db.Integer,
                   primary_key=True)
    overused_word = db.Column(db.Integer, db.ForeignKey(
        'overused_word.id'), nullable=False)
    cluster = db.Column(db.String())
    sentence_start = db.Column(db.Integer)
    sentence_end = db.Column(db.Integer)

    def __init__(self, overused_word, cluster, sentence_start, sentence_end):
        self.overused_word = overused_word
        self.cluster = cluster
        self.sentence_start = sentence_start
        self.sentence_end = sentence_end
