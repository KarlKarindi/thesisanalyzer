from .general import mod as general_mod
from .style import mod as style_mod


def init_app(app):
    app.register_blueprint(general_mod)
    app.register_blueprint(style_mod)
