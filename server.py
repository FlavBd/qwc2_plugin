# -*- coding: utf-8 -*-
import os
import json
import requests
import io
import zipfile
from flask import Flask, request, send_file
from flask_jwt_extended import jwt_optional, get_jwt_identity, jwt_required
from qwc_services_core.jwt import jwt_manager

QGIS_PROJECT_DIRECTORY = '/opt/qgis-server/'
PLUGIN_DIRECTORY = '/opt/qwc2/qwc-services/qwc2_plugin/plugin'
CONFIG_FILE = '/opt/qwc2/qwc-services/config-in/default/tenantConfig.json'
QGIS_SERVER_URL = 'https://qgisweb.oslandia.net' #TODO get that from request url because this service runs on the same server as qgis-server

# Flask application
app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
jwt = jwt_manager(app)

@app.route('/get_config', methods=['GET'])
@jwt_required
def get_config():
    """Get configuration file from config-generator service

    Return config file as JSON text
    ---
    TODO :
    - set CONFIG_FILE with env variables INPUT_CONFIG_PATH, CONFIG_GENERATOR_CONFIG and tenant name
    """
    print("Identity : ", get_jwt_identity())
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    return config

@app.route('/set_project', methods=['POST'])
@jwt_required
def set_project():
    """Set QGIS project file to QGIS_PROJECT_DIRECTORY location
    ---
    TODO :
    - set QGIS_PROJECT_DIRECTORY with env variable
    """
    print("Identity : ", get_jwt_identity())
    if 'project_file' in request.files:
        f = request.files['project_file']
        f.save(os.path.join(QGIS_PROJECT_DIRECTORY, f.filename))
    return "OK", 200

@app.route('/set_config', methods=['POST'])
@jwt_required
def set_config():
    """Save new configuration file from config-generator service
    ---
    TODO :
    - set config-generator-service url in service configuration
    """
    print("Identity : ", get_jwt_identity())
    with open(CONFIG_FILE, 'w') as f:
        json.dump(request.json, f, indent=4)
    url = request.url_root.replace(request.script_root, '')
    r = requests.post(url+'/config_gen/generate_configs?tenant=default')
    if r.status_code != 200:
        print("attempting to generate config, the server request returned code {}".format(r.status_code))
        print(r.text)
        return r.text
    return "OK", 200

@app.route('/download', methods=['GET'])
def download():
    """Download plugin directory as zip file
    ---
    TODO :
    - set PLUGIN_DIRECTORY with env variable
    """    
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for filename in os.listdir(PLUGIN_DIRECTORY):
            z.write(os.path.join(PLUGIN_DIRECTORY, filename), filename)
    data.seek(0)
    return send_file(data, mimetype='application/zip', as_attachment=True, attachment_filename='qwc2_plugin.zip')

if __name__ == "__main__":
    app.run(debug=True)