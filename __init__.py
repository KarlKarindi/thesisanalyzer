from flask import Flask

def create_app():
    from . import routes, services
    app = Flask(__name__)
    routes.init_app(app)
    print("App creation successful.")
    return app