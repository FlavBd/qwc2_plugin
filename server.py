# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, make_response, redirect, jsonify
import os
import json
import logging
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_jwt_extended import jwt_optional, get_jwt_identity, create_access_token, create_refresh_token, \
    set_access_cookies, unset_jwt_cookies, jwt_required, set_refresh_cookies
from qwc_services_core.jwt import jwt_manager
from qwc_services_core.database import DatabaseEngine
from qwc_services_core.config_models import ConfigModels
from qwc_services_core.permissions_reader import PermissionsReader
from qwc_services_core.runtime_config import RuntimeConfig
from qwc_services_core.tenant_handler import TenantHandler
from qwc2_plugin import QWC2PluginService

QGIS_PROJECT_DIRECTORY = '/tmp'
QWC2_THEME_CONFIG = '/opt/qwc2/themesConfig.json'
QGIS_SERVER_URL = 'http://qgisweb.oslandia.net' #TODO get that from request url because this service runs on the same server as qgis-server

# Flask application
app = Flask(__name__)

login = LoginManager(app)

# create tenant handler
tenant_handler = TenantHandler(app.logger)

# Setup the Flask-JWT-Extended extension
jwt = jwt_manager(app)

def qwc2_plugin_service_handler():
    """Get or create a QWC2PluginService instance for a tenant."""
    tenant = tenant_handler.tenant()
    handler = tenant_handler.handler('qwc2plugin', 'qwc2plugin', tenant)
    if handler is None:
        handler = tenant_handler.register_handler(
            'qwc2plugin', tenant, QWC2PluginService(tenant, app.logger))
    return handler

@app.route('/config', methods=['GET', 'POST'])
@jwt_required
def index():
    qwc2_plugin_service = qwc2_plugin_service_handler()
    return qwc2_plugin_service.qwc2_identity(get_jwt_identity())
# def index():
#     qwc2_plugin_service = qwc2_plugin_service_handler()
#     tenant = tenant_handler.tenant()
#     handler = tenant_handler.handler('mapViewer', 'qwc', tenant)
#     config_handler = RuntimeConfig("mapViewer", app.logger)
#     config = config_handler.tenant_config(tenant)
#     permissions_handler = PermissionsReader(tenant, app.logger)

#     # load resources
#     qwc2_config = config.resources().get('qwc2_config', {})
#     qwc2_themes = config.resources().get('qwc2_themes', {})
#     qwc2_themes = qwc2_themes.get('themes', {})
#     resources = {'qwc2_config': qwc2_config, 'qwc2_themes': qwc2_themes}
#     print(get_jwt_identity())

#     # load themes for user
#     themes = json.loads(json.dumps(resources['qwc2_themes']))

#     # filter theme items by permissions
#     items = []
#     for item in themes['items']:
#         # get permissions for WMS
#         wms_permissions = permissions_handler.resource_permissions(
#             'wms_services', get_jwt_identity(), item['wms_name']
#         )
#         if not wms_permissions:
#             print(item['wms_name'] + ' not permitted for user ' + get_jwt_identity())
#             continue
#         # combine permissions
#         permitted_layers = set()
#         permitted_print_templates = set()
#         for permission in wms_permissions:
#             # collect permitted layers
#             permitted_layers.update([
#                 layer['name'] for layer in permission['layers']
#             ])
#             # collect permitted print templates
#             permitted_print_templates.update(
#                 permission.get('print_templates', [])
#             )
#         permitted_item = item
#         if permitted_item:
#             items.append(permitted_item)
    
#     themes['items'] = items
#     print(themes)

#     print(request)
#     if request.method == 'POST':

#         if 'project_file' in request.files:
#             f = request.files['project_file']
#             print(f.filename)
#             f.save(os.path.join(QGIS_PROJECT_DIRECTORY, f.filename))

#         if request.json is not None:
#             with open(QWC2_THEME_CONFIG, 'w') as c:
#                 json.dump(request.json, c, indent=4)

#         return "OK", 200

#     else:
#         with open(QWC2_THEME_CONFIG) as f:
#             config = json.load(f)
#         return config, 200

@app.route('/connect', methods=['GET', 'POST'])
def connect():
    print(get_jwt_identity())
    target_url = request.args.get('url', '/')
    db_engine = DatabaseEngine()
    db_url = "postgresql:///?service=qwc_configdb"
    config_models = ConfigModels(db_engine, db_url)
    User = config_models.model('users')

    db_session = config_models.session()

    url = request.url
    username = request.values['username']
    password = request.values['password']

    user = db_session.query(User).filter_by(name=username).first()
    if user is None:
        print("User doesn't exist.")
    elif user.check_password(password):
        db_session.commit()
        login_user(user)
        # Create the tokens we will be sending back to the user
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        resp = jsonify({'login': True})
        # Set the JWTs and the CSRF double submit protection cookies in this response
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        print("User connected")
        print(get_jwt_identity())
    else:
        db_session.commit()
        print("Invalid password")

    db_session.close()
    print(get_jwt_identity())

    return 'OK'



if __name__ == "__main__":
    app.run(debug=True)