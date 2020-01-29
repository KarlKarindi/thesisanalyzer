from . import Feedback

def init_app(app):
    app.register_blueprint(Feedback)
