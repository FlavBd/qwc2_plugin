import os
import re
from urllib.parse import urljoin, urlencode, urlparse
from xml.etree import ElementTree

from flask import Response, stream_with_context
import requests

from qwc_services_core.permissions_reader import PermissionsReader
from qwc_services_core.runtime_config import RuntimeConfig

class QWC2PluginService:
    """OGCSeQWC2PluginService class
    """

    def __init__(self, tenant, logger):
        """Constructor
        :param str tenant: Tenant ID
        :param Logger logger: Application logger
        """
        self.tenant = tenant
        self.logger = logger

        config_handler = RuntimeConfig("qwc2plugin", logger)
        config = config_handler.tenant_config(tenant)

        self.resources = self.load_resources(config)
        self.permissions_handler = PermissionsReader(tenant, logger)
    
    def qwc2_identity(self, identity):
        """Return QWC2 index.html for user.
        :param obj identity: User identity
        """
        return identity