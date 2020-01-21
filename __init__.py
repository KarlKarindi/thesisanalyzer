from flask import Flask
from estnltk import Vabamorf

# Initialize vabamorf singleton
vabamorf = Vabamorf.instance()


def create_app():
    from . import routes, services, model
    app = Flask(__name__)
    routes.init_app(app)
    print("App update/creation successful.\n\n\n")
    return app
