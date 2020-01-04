from flask import Flask
import simplejson as json
import estnltk

app = Flask(__name__)

print(estnltk.Text("Hi estnltk"))


@app.route("/")
def hello():
    return "Hello world"


if __name__ == "__main__":
    app.run(debug=True)
