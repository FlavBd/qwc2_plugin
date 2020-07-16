# -*- coding: utf-8 -*-

import requests
import sys
import os

url = "http://localhost:5000/config"
filename = sys.argv[1] if len(sys.argv) >= 2 else None

r = requests.get(url)
config = r.json()

print (config['themes']['items'][0])
print("#####################")

# modif config

if filename is not None:
    r = requests.post(url, files={'project_file': (os.path.basename(filename), open(filename, 'rb'), 'application/xml')})
    r = requests.post(url, headers={'content-Type': 'application/json'}, json=config)
else:
    r = requests.post(url, headers={'content-Type': 'application/json'},json=config)

print(r)