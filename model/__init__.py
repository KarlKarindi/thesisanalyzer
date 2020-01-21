from . import generalFeedback
from . import styleFeedback

def init_app(app):
    app.register_blueprint(generalFeedback)
    app.register_blueprint(styleFeedback)
