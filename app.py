from flask import Flask, request
import simplejson as json
import utils as utils
import service as service

app = Flask(__name__)

@app.route('/style/', methods=['POST'])
def style_controller():
    return service.analyze_style(utils.json_to_text(request))

@app.route('/general/', methods=['POST'])
def general_controller():
    return service.analyze_general(utils.json_to_text(request))

if __name__ == "__main__":
    app.run(debug=True)
