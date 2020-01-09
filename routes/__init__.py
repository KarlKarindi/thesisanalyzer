from .general import gen_bp
from .style import style_bp

def init_app(app):
    app.register_blueprint(gen_bp)
    app.register_blueprint(style_bp)