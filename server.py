# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import os
import json


QGIS_PROJECT_DIRECTORY = '/tmp'
QWC2_THEME_CONFIG = '/tmp/themesConfig.json'
QGIS_SERVER_URL = 'http://qgisweb.oslandia.net' #TODO get that from request url because this service runs on the same server as qgis-server

# Flask application
app = Flask(__name__)

@app.route('/config', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        if 'project_file' in request.files:
            f = request.files['project_file']
            f.save(os.path.join(QGIS_PROJECT_DIRECTORY, f.filename))

        if request.json is not None:
            print(request.json)
            with open(QWC2_THEME_CONFIG, 'w') as c:
                json.dump(request.json, c, indent=4)

        return "OK", 200

    else:
        with open(QWC2_THEME_CONFIG) as f:
            config = json.load(f)
            print(config)
        return config, 200

    # update config



if __name__ == "__main__":
    app.run(debug=True)