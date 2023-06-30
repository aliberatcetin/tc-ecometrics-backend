import csv
import json
import os
from kink import di
import pandas as pd
import xlrd as xlrd
from flask import Flask, request
from io import StringIO, BytesIO
from mongoengine import connect
from flask import Blueprint
from openpyxl import load_workbook

from History import History
from calculations import Calculations
from di_container import initialize_context
from file_manager import FileManager

blueprint = Blueprint('blueprint', __name__)
app = Flask(__name__)
calculator = Calculations()
string = os.environ["MONGO_CONNECTION_STRING"]
a = connect(
    host=string
)


# put this sippet ahead of all your bluprints
# blueprint can also be app~~
@blueprint.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    # Other headers can be added here if needed
    return response


@blueprint.route("/history", methods=["GET"])
def history():
    return History.objects().to_json(), 200, {"content-type": "application/json"}


@blueprint.route("/history/<id>", methods=["GET"])
def history_by_id(id):
    history_objects = History.objects(calculation_id=id).all()
    if len(history_objects) > 0:
        history_object = json.loads(history_objects[0].to_json())
    else:
        history_object = []

    history_object["ne"]="asdas"
    history_object["recommendations"] = di[FileManager].get_recommendation_json()
    return history_object, 200, {"content-type": "application/json"}


@blueprint.route('/csv', methods=['POST'])
def index():
    data = []
    if request.method == 'POST':
        if request.files:
            uploaded_file = request.files['csvfile']  # This line uses the same variable and worked fine
            # wb = xlrd.open_workbook(path, encoding_override='CORRECT_ENCODING')
            file = pd.ExcelFile(BytesIO(uploaded_file.read()))
            doc = calculator.calculate_mobility_scores(file)
            History(**doc).save()
            doc["recommendations"] = di[FileManager].get_recommendation_json()
            return doc

    return "asd"


if __name__ == "__main__":
    initialize_context()
    app.register_blueprint(blueprint)
    app.run(port=3002, debug=True)
