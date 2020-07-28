# -*- coding: utf-8 -*-
import os
import json
import requests
from flask import Flask, request
from flask_jwt_extended import jwt_optional, get_jwt_identity, jwt_required
from qwc_services_core.jwt import jwt_manager

QGIS_PROJECT_DIRECTORY = '/opt/qgis-server/'
CONFIG_FILE = '/opt/qwc2/qwc-services/config-in/default/tenantConfig.json'
QGIS_SERVER_URL = 'http://qgisweb.oslandia.net' #TODO get that from request url because this service runs on the same server as qgis-server

# Flask application
app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
jwt = jwt_manager(app)

@app.route('/get_config', methods=['GET'])
@jwt_required
def get_config():
    print("Identity : ", get_jwt_identity())
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    return config

@app.route('/set_project', methods=['POST'])
@jwt_required
def set_project():
    print("Identity : ", get_jwt_identity())
    if 'project_file' in request.files:
        f = request.files['project_file']
        f.save(os.path.join(QGIS_PROJECT_DIRECTORY, f.filename))
    return "OK", 200

@app.route('/set_config', methods=['POST'])
@jwt_required
def set_config():
    print("Identity : ", get_jwt_identity())
    with open(CONFIG_FILE, 'w') as f:
        json.dump(request.json, f)
    url = request.url_root.replace(request.script_root, '')
    r = requests.post(url+'/config_gen/generate_configs?tenant=default')
    if r.status_code != 200:
        print("attempting to get config, the server request returned code {}".format(r.status_code))
        print(r.text)
        return r.text
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)