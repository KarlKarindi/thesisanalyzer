from ThesisAnalyzer.Models import Feedback
from ThesisAnalyzer.Models import Lemma


def init_app(app):
    app.register_blueprint(Feedback)
    app.register_blueprint(Lemma)
