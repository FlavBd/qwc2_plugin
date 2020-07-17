from qgis.PyQt.QtWidgets import QDialog, QWidget, QPushButton, QVBoxLayout, QCheckBox
from qgis.PyQt import uic
from qgis.core import QgsSettings
#from urllib import requests
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

        # autres test pour savoir si qgis server project
        if self.urlLineEdit.text():
            self.__getConfig()
        

    def __getConfig(self):
        self.projectsComboBox.clear()
        self.__projectIdxInConfig = None

        r = requests.get(self.urlLineEdit.text()+'/config')
        if r.status_code != 200:
            self.warningLabel.setText("attempring to get server config, the server request returned code {}".format(r.status_code))
            return
        self.__config = r.json()

        #Afficher les projets du themesConfig dans la boite de dialog Projects
        currentProject = os.path.splitext(os.path.basename(self.__currentQgisProjectFile))[0]
        projects = []
        for i, item in enumerate(self.__config['themes']['items']):
            project = item['url'].split("/")[-1]
            projects.append(project)
            if project == currentProject:
                self.__projectIdxInConfig = i

        if self.__projectIdxInConfig is None:
            self.__config['themes']['items'].append({
                "url": self.urlLineEdit.text()+'/'+currentProject,
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
            self.__projectIdxInConfig = len(self.__config['themes']['items']) - 1
            projects = [currentProject] + projects

        self.projectsComboBox.addItems(projects)

    def __projectChanged(self, selection):        
        # save previous ProjectConfig
        if self.__projectConfig is not None:
            if self.__projectIdxInConfig is not None:
                self.__config['themes']['items'][self.__projectIdxInConfig] = self.__projectConfig.item()
            self.__projectConfig.setParent(None)
            self.__projectConfig = None


        # replace ProjectConfig
        for i, item in enumerate(self.__config['themes']['items']):
            if item['url'].split("/")[-1] == selection: # /!\ assumes qgs projet name is at the end of url
                self.__projectIdxInConfig = i
                print("found", i)
                break
        if self.__projectIdxInConfig is not None:
            self.__projectConfig = ProjectWidget(
                self.__config['themes']['items'][self.__projectIdxInConfig],
                self.__config['themes']['backgroundLayers'])
            self.__projectConfig.show()  
            self.projectsGroupBox.layout().addWidget(self.__projectConfig)

  
    def accept(self):
        s = QgsSettings()
        s.setValue("qwc2configurator/server/url", self.urlLineEdit.text())
        s.setValue("qwc2configurator/server/username", self.usernameLineEdit.text())
        s.setValue("qwc2configurator/server/password", self.passwordLineEdit.text())

        if self.__projectConfig is not None:
        
            self.__config['themes']['items'][self.__projectIdxInConfig] = self.__projectConfig.item()
            
            #Vérification authentification server
            r = requests.post(self.urlLineEdit.text()+'/config', files={'project_file': (os.path.basename(self.__currentQgisProjectFile), open(self.__currentQgisProjectFile, 'rb'), 'application/xml')})
            if r.status_code != 200:
                self.warningLabel.setText("attempting to send qgis project, the server request returned code {}".format(r.status_code))
                return        
            r = requests.post(self.urlLineEdit.text()+'/config', headers={'content-Type': 'application/json'}, json=self.__config)
            if r.status_code != 200:
                self.warningLabel.setText("attempting to save the config, the server request returned code {}".format(r.status_code))
                return
        
        super(ConfigDialog, self).accept()

    
if __name__ == "__main__":
    from qgis.core import QgsApplication
    import sys
    a = QgsApplication([], False)
    a.initQgis()

    d = ConfigDialog(sys.argv[1] if len(sys.argv) >= 2 else None)

    d.show()
    a.exec()