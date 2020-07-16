import json
import os
import sys
from themeConfig import genThemes


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


def generateTheme(theme_config_filename, qgis_projects_directory):
    print(os.getcwd())

    projects=[]
    # Get list of files to generate items
    with os.scandir(qgis_projects_directory) as files:
        for f in files:
            if f.is_file and f.name.endswith(".qgs"):
                projects.append(f.name)
    print(projects)

    # Load model to generate new themesConfig.json
    with open("./model.json") as f:
        config=json.load(f)
    print(config)
    print("----------------------------------------------------------")

    # Loop on files to generate items
    for project in projects:
        generateItem(project)

    print(config)
    config.pop("project", None)
    print(config)

    # Save new themesConfig.json
    with open(os.environ.get("QWC2_THEMES_CONFIG", filename),"w") as f:
        json.dump(config,f,indent=2,separators=(',',': '))

    #os.environ["QWC2_THEMES_CONFIG"] = "{{ __qwc2_dir__ }}/{{ __themes_config_file__ }}"

    genThemes(filename)