from flask import Flask

def create_app():
    from . import routes, services
    app = Flask(__name__)
    routes.init_app(app)
    print("done")
    #services.init_app(app)
    return app