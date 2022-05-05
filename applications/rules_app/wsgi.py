import json
from flask import Flask, jsonify, request
from prediction import predict

application = Flask(__name__)


@application.route('/')
@application.route('/status')
def status():
    return jsonify({'status': 'ok'})


@application.route('/validate', methods=['POST'])
def validation():
    data = request.data or '{}'
    body = json.loads(data)
    return jsonify(validate(body))
