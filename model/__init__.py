from .feedback import FeedBack

def init_app(app):
    app.register_blueprint(FeedBack)