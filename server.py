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
                json.dump(request.json, c)

        return "OK", 200

    else:
        with open(QWC2_THEME_CONFIG) as f:
            config = json.load(f)
            print(config)
        return config, 200

    # update config


# Function to generate one item in items dictionary 
def generateItem(project):
    item={}
    scales=[]
    backgroundLayers=[]
    searchProviders=[]
    additionalMouseCrs=[]
    item["url"]=config["project"]["url"]+os.path.splitext(os.path.basename(project))[0]
    item["attribution"]=config["project"]["attribution"]
    item["attributionUrl"]=config["project"]["attributionUrl"]
    item["format"]="image/png; mode=8bit"
    item["default"]= True
    scales=config["defaultScales"]
    item["scales"]=[]
    for i in scales:
        item["scales"].append(i)
    backgroundLayers=config["themes"]["backgroundLayers"]
    item["backgroundLayers"]=[]
    for i in backgroundLayers:
        layer={}
        layer["name"]=i["name"]
        layer["visibility"]=True
        item["backgroundLayers"].append(layer)
    searchProviders=config["project"]["searchProviders"]
    item["searchProviders"]=[]
    for i in searchProviders:
        item["searchProviders"].append(i)
    item["mapCrs"]=config["project"]["mapCrs"]
    additionalMouseCrs=config["project"]["additionalMouseCrs"]
    item["additionalMouseCrs"]=[]
    for i in additionalMouseCrs:
        item["additionalMouseCrs"].append(i)
    item["collapseLayerGroupsBelowLevel"]= 1
    config["themes"]["items"].append(item)


if __name__ == "__main__":
    app.run(debug=True)