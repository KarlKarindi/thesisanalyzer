from ThesisAnalyzer.Routes.routes import mod


def init_app(app):
    app.register_blueprint(mod)
