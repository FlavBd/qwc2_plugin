from qgis.PyQt.QtWidgets import QDialog, QWidget, QPushButton, QVBoxLayout, QCheckBox
from qgis.PyQt import uic
from qgis.core import QgsSettings, QgsMessageLog, Qgis
from subprocess import Popen, check_output, PIPE
import os
import sys
import requests

from .project_dialog import ProjectWidget

class ConfigDialog(QDialog):
    def __init__(self, currentQgisProjectFile, parent=None):
        super(ConfigDialog, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "config_dialog.ui"), self)
        
        assert(currentQgisProjectFile and os.path.isfile(currentQgisProjectFile))
        if currentQgisProjectFile is not None and not currentQgisProjectFile.endswith(".qgs"):
            self.warningLabel.setText("the project extension is not .qgs")

        s = QgsSettings()

        self.urlLineEdit.setText(s.value("qwc2configurator/server/url",""))
        self.usernameLineEdit.setText(s.value("qwc2configurator/server/username",""))
        self.passwordLineEdit.setText(s.value("qwc2configurator/server/password",""))
            
        self.__config = None
        self.__projectIdxInConfig = None
        self.__projectConfig = None
        self.__currentQgisProjectFile = os.path.abspath(currentQgisProjectFile)

        self.projectsComboBox.currentIndexChanged[str].connect(self.__projectChanged)
        self.getConfigButton.clicked.connect(self.__getConfig)

    def __getConfig(self):
        s = QgsSettings()
        self.projectsComboBox.clear()
        self.__projectIdxInConfig = None
        s.setValue("qwc2configurator/server/url", self.urlLineEdit.text())
        s.setValue("qwc2configurator/server/username", self.usernameLineEdit.text())
        s.setValue("qwc2configurator/server/password", self.passwordLineEdit.text())
        url = self.urlLineEdit.text()

        session = self.__createSession()
        # You can optionally pass a 'tag' and a 'level' parameters
        r = session.get(url+'/plugin/get_config')
        if r.status_code != 200:
            QgsMessageLog.logMessage("attempting to get server config, the server request returned code {}".format(r.status_code), 'QWC2 Plugin', level=Qgis.Critical)
            self.warningLabel.setText("attempting to get server config, the server request returned code {}".format(r.status_code))
            return
        self.__config = r.json()

        #Afficher les projets du themesConfig dans la boite de dialog Projects
        currentProject = os.path.splitext(os.path.basename(self.__currentQgisProjectFile))[0]
        projects = []
        for i, item in enumerate(self.__config['themesConfig']['themes']['items']):
            project = item['url'].split("/")[-1]
            projects.append(project)
            if project == currentProject:
                self.__projectIdxInConfig = i

        if self.__projectIdxInConfig is None:
            self.__config['themesConfig']['themes']['items'].append({
                "url": self.urlLineEdit.text()+'/qgis/'+currentProject,
                "scales": [4000000, 2000000, 1000000, 400000, 200000, 80000, 40000, 20000, 10000, 8000, 6000, 4000, 2000, 1000, 500, 250, 100],
                "attribution": "",
                "attributionUrl": "",
                "format": "image/png; mode=8bit",
                "default": False,
                "backgroundLayers": [],
                "searchProviders": [],
                "mapCrs": "EPSG:3857",
                "additionalMouseCrs": [],
                "collapseLayerGroupsBelowLevel": 1
            })
            self.__projectIdxInConfig = len(self.__config['themesConfig']['themes']['items']) - 1
            projects = [currentProject] + projects

        self.projectsComboBox.addItems(projects)

    def __projectChanged(self, selection):        
        # save previous ProjectConfig
        if self.__projectConfig is not None:
            if self.__projectIdxInConfig is not None:
                self.__config['themesConfig']['themes']['items'][self.__projectIdxInConfig] = self.__projectConfig.item()
            self.__projectConfig.setParent(None)
            self.__projectConfig = None


        # replace ProjectConfig
        for i, item in enumerate(self.__config['themesConfig']['themes']['items']):
            if item['url'].split("/")[-1] == selection: # /!\ assumes qgs projet name is at the end of url
                self.__projectIdxInConfig = i
                break
        if self.__projectIdxInConfig is not None:
            self.__projectConfig = ProjectWidget(
                self.__config['themesConfig']['themes']['items'][self.__projectIdxInConfig],
                self.__config['themesConfig']['themes']['backgroundLayers'])
            self.__projectConfig.show()  
            self.projectsGroupBox.layout().addWidget(self.__projectConfig)

    def __createSession(self):
        s = QgsSettings()
        session = requests.Session()
        url = self.urlLineEdit.text()
        username = s.value("qwc2configurator/server/username")
        password = s.value("qwc2configurator/server/password")
        r = session.post(
            url + '/auth/login?url=' + url + '/admin',
                {"username": username, "password": password})
        return session
  
    def accept(self):
        s = QgsSettings()
        s.setValue("qwc2configurator/server/url", self.urlLineEdit.text())
        s.setValue("qwc2configurator/server/username", self.usernameLineEdit.text())
        s.setValue("qwc2configurator/server/password", self.passwordLineEdit.text())

        if self.__projectConfig is not None:
        
            self.__config['themesConfig']['themes']['items'][self.__projectIdxInConfig] = self.__projectConfig.item()
            
            #Vérification authentification server
            session = self.__createSession()

            r = session.post(self.urlLineEdit.text()+'/plugin/set_project', files={'project_file': (os.path.basename(self.__currentQgisProjectFile),open(self.__currentQgisProjectFile, 'rb'), 'application/xml')})
            if r.status_code != 200:
                QgsMessageLog.logMessage("attempting to send qgis project, the server request returned code {}".format(r.status_code), 'QWC2 Plugin', level=Qgis.Critical)
                self.warningLabel.setText("attempting to send qgis project, the server request returned code {}".format(r.status_code))
                return
            else:
                QgsMessageLog.logMessage("QGIS project has been sent to the server", 'QWC2 Plugin', level=Qgis.Success)
            r = session.post(self.urlLineEdit.text()+'/plugin/set_config', headers={'content-Type': 'application/json'}, json=self.__config)
            if r.status_code != 200:
                QgsMessageLog.logMessage("attempting to save new configuration, the server request returned code {}".format(r.status_code), 'QWC2 Plugin', level=Qgis.Critical)
                self.warningLabel.setText("attempting to save the config, the server request returned code {}".format(r.status_code))
                return
            else:
                QgsMessageLog.logMessage("New configuration has been saved", 'QWC2 Plugin', level=Qgis.Success)
        
        super(ConfigDialog, self).accept()

    
if __name__ == "__main__":
    from qgis.core import QgsApplication
    import sys
    a = QgsApplication([], False)
    a.initQgis()

    d = ConfigDialog(sys.argv[1] if len(sys.argv) >= 2 else None)

    d.show()
    a.exec()