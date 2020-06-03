# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import sys
from pathlib import Path

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

try:
    sys.path.remove(str(parent))
except ValueError: # Already removed
    pass

from src.response import get_response
from src.constants import COUNTRIES, CLASSES, WAY_LS
from src.utilities import PrepUtility
import flask_sijax
import os
from src.utilities import write_json
import time
from nlu.run_multi_task_rnn import Model, read_data_test
from nlu.data_utils import prepare_multi_task_data

root = Path(os.path.abspath(__file__)).parent.parent
test_seq_in_path = str(root) + '/data/ATIS_samples/test/test.seq.in'

path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
app = Flask(__name__)
app.config['SIJAX_STATIC_PATH'] = path
app.config['SIJAX_JSON_URI'] = '../static/js/sijax/json2.js'
flask_sijax.Sijax(app)

model = Model()
data_path = str(root) + '/data/ATIS_samples'

# Chatting api
@app.route("/api/query")
def query():
    message = str(request.args.get('message'))
    for way in WAY_LS:
        if way in message:
            message = message.replace("-", " ")
    user_in = PrepUtility.create_test_seq_in(message)
    PrepUtility.prepareNLUMessage(user_in, test_seq_in_path)
    date_set = prepare_multi_task_data(data_path, 10000, 10000)
    date_set = list(date_set)
    in_seq_test, out_seq_test, label_test = date_set[2]
    test_set = read_data_test(in_seq_test, out_seq_test, label_test)
    start = time.time()
    predictions = model.predict(test_set)
    #print(time.time()-start)
    response = get_response(message)
    return jsonify(response)


@app.route("/api/countries")
def countries():
    response = dict(countries=COUNTRIES, classes=CLASSES)
    return jsonify(response)


# Load chatting page
@app.route('/')
def index():
    return render_template('chat.html')


if __name__ == "__main__":
    date_set = prepare_multi_task_data(data_path, 10000, 10000)
    date_set = list(date_set)
    in_seq_test, out_seq_test, label_test = date_set[2]
    test_set = read_data_test(in_seq_test, out_seq_test, label_test)
    model.predict(test_set)
    write_json(dict(), "ticket.json")
    app.run(debug=False, port=1234)
