from qgis.PyQt.QtWidgets import QDialog, QWidget, QPushButton, QVBoxLayout, QCheckBox
from qgis.PyQt import uic
from qgis.core import QgsSettings
#from urllib import requests
from subprocess import Popen, check_output, PIPE
import os
import sys
import requests

class ConfigDialog(QWidget):
    def __init__(self, currentQgisProjectFile, parent=None):
        super(ConfigDialog, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "./templates/config_dialog2.ui"), self)
        s = QgsSettings()
        self.urlLineEdit.setText(s.value("qwc2configurator/server/url",""))
        self.usernameLineEdit.setText(s.value("qwc2configurator/server/username",""))
        self.passwordLineEdit.setText(s.value("qwc2configurator/server/password",""))
        self.currentQgisProjectFile = currentQgisProjectFile
        if self.currentQgisProjectFile is None or not os.path.isfile(self.currentQgisProjectFile):
            self.warningLabel.setText("there is no current QGIS project file")
        if self.currentQgisProjectFile is not None and not self.currentQgisProjectFile.endswith(".qgs"):
            self.warningLabel.setText("the project extension is not .qgs")
        # autres test pour savoir si qgis server project

        self.background_name = []  


        self.__udpateProjects()

    def __udpateProjects(self):
        # if self.urlLineEdit.text().endswith("/"):
        #     url = self.urlLineEdit.text() + "config"
        # else: 
        #     url = self.urlLineEdit.text() + "/config"

        url = "http://localhost:5000/config"

        r = requests.get(url)
        if r.status_code != 200:
            self.warningLabel.setText("attempring to get server config, the server request returned code ", r.code)
            return False
        self.config = r.json()

        print(self.config)

        #Afficher les projets du themesConfig dans la boite de dialog Projects
        if self.projectsComboBox.count() == 0:
            for i in self.config['themes']['items']: 
                url = i['url']
                self.project = url.split("/")[-1]
                self.projectsComboBox.addItem(self.project)
            self.projectsComboBox.addItem(os.path.splitext(self.currentQgisProjectFile)[0])
            self.projectsComboBox.setCurrentIndex(-1)
        
        self.projectsComboBox.currentIndexChanged[str].connect(self.__recoverProjects)
        
        # définir les valeurs

        # si le projet courant n'est pas dans les items, créer un premier formulaire project
        #self.project_widgets = [ProjectConfig()] # utiliser le conteur Qt comme tableau

        # boucler sur les items et créer les widgets
        # for item in config['themes']['items']:
        #     self.project.append(ProjectConfig(item[i]))


        # return True

    def __recoverProjects(self, selection):
        #Vérifier si title vide, si non enregistrer info projets
            # saveProject --> enregistre les infos dans le thème config
            # fonction qui efface toutes les valeurs
        
        #create new themesConfig.json
        if not self.projectGroupBox.title() == "":
            self.__saveProjects(self.projectGroupBox.title(), self.background_name)

        #initialise items
        self.__initialiseItems()

        #Récupère nom projet pour title
        self.selected_project = selection
        self.projectGroupBox.setTitle(self.selected_project)
        print(selection)

        if self.selected_project == os.path.splitext(self.currentQgisProjectFile)[0]:
            for layer in self.config['themes']['backgroundLayers']: 
                name = layer['name']
                self.checkBox = QCheckBox(name)
                self.checkBox.setText(name)
                self.backgroundLayout.addWidget(self.checkBox)
                newHeight = self.geometry().height()+21
                self.resize(self.geometry().width(), newHeight)
        else:           
            #récupérer valeurs du projet avant
            self.scales = [item['scales'] for item in self.config['themes']['items'] if item['url'].endswith(self.selected_project)]
            self.scaleLineEdit.setText(str(self.scales).strip())
            print(self.scales)      
                
            self.background = [item['backgroundLayers'] for item in self.config['themes']['items'] if item['url'].endswith(self.selected_project)]
            print(self.background)
            for layer in self.config['themes']['backgroundLayers']: 
                name = layer['name']
                self.checkBox = QCheckBox(name)
                self.checkBox.setText(name)
                self.backgroundLayout.addWidget(self.checkBox)
                newHeight = self.geometry().height()+21
                self.resize(self.geometry().width(), newHeight)
                for item in self.background:
                    if item['name'] == self.checkBox.text():
                        self.backgroundLayout.addWidget(self.checkBox.setChecked(True))
                        self.background_name.append(item['name'])

            # when background is deleted (not check), delete from Combobox
            for item in self.background:
                background_name = item['name']
                self.backgroundComboBox.addItem(background_name)
                if item['visibility'] == True:
                    self.backgroundComboBox.setCurrentText(background_name)

            self.searchProviders = [item['searchProviders'] for item in self.config['themes']['items'] if item['url'].endswith(self.selected_project)]

            for item in self.searchProviders:
                if item == 'coordinates':
                    self.coordinatesCheckBox.setChecked(True)
                if item == 'nominatim':
                    self.nominatimCheckBox.setChecked(True)
                
    
    def __saveProjects(self,project,background_name):
        print(project)
        for item in self.config['themes']['items']:
            if item['url'].endswith(project):
                item['scales'] = self.scaleLineEdit.text().split(',') #problem : delete first and last character
                item['backgroundLayers'] = []
                for i in self.background_name: #problem when background is added 
                    layer={}
                    layer['name']=i
                    if self.backgroundComboBox.currentText() == i:
                        layer['visibility']=True
                    else:
                        layer['visibility']=False
                    item['backgroundLayers'].append(layer)
                item["searchProviders"]=[]
                if self.coordinatesCheckBox.isChecked() == True:
                    item["searchProviders"].append("coordinates")
                if self.nominatimCheckBox.isChecked() == True:
                    item["searchProviders"].append("nominatim")
                
        if project == os.path.splitext(self.currentQgisProjectFile)[0]:
            item['url'] = self.urlLineEdit.text() + os.path.splitext(self.currentQgisProjectFile)[0]
           
        # print(self.config)
    
    def __initialiseItems(self):
        for i in reversed(range(self.backgroundLayout.count())):
                    widgetToRemove = self.backgroundLayout.itemAt(i).widget()
                    # remove it from the layout list
                    self.backgroundLayout.removeWidget(widgetToRemove)
                    # remove it from the gui
                    widgetToRemove.setParent(None)
        
        self.background_name = []
        self.backgroundComboBox.clear()

        self.coordinatesCheckBox.setChecked(False)
        self.nominatimCheckBox.setChecked(False)

    
    def accept(self):
        s = QgsSettings()
        s.setValue("qwc2configurator/server/url", self.urlLineEdit.text())
        s.setValue("qwc2configurator/server/username", self.usernameLineEdit.text())
        s.setValue("qwc2configurator/server/password", self.passwordLineEdit.text())

        if not self.__udpateProjects():
            return
        
        #Vérification authentification server

        # mise à jour de self.config en fonction des valeurs des champs du formulaire
        
        # for f in self.config['themes']['items'] if f['url'].endswith(self.selected_project)][0]
        # self.config['themes']['items'] self.scaleLineEdit.text() 

        if  self.currentQgisProjectFile is not None:
            r = requests.post(url, files={'project_file': (os.path.basename( self.currentQgisProjectFile), open( self.currentQgisProjectFile, 'rb'), 'application/xml')})
            if r.code != 200:
                self.warningLabel.setText("attempting to upload the project file, the server returned code", r.code)
                return        
        r = requests.post(url, headers={'content-Type': 'application/json'}, json=config)
        if r.code != 200:
            self.warningLabel.setText("attempting to save the config, the server request returned code ", r.code)
            return
    
    def publishProject(self):
        self.accept()
        print("on publie")
        s = QgsSettings()
    
    # def listerprojet qui construit les formulaires
    #     requete sur serveur : build project form, clear les formulaires et les reconstruit

# print(r)
    
#     def fonction qui renvoie le json complet

if __name__ == "__main__":
    from qgis.core import QgsApplication
    import sys
    a = QgsApplication([], False)
    a.initQgis()
    d = QDialog()
    d.resize(800, 600)
    l = QVBoxLayout()
    d.setLayout(l)
    b = QPushButton("Accept")
    w = ConfigDialog(sys.argv[1] if len(sys.argv) >= 2 else None)
    b.clicked.connect(w.accept)
    l.addWidget(w)
    l.addWidget(b)
    d.show()
    a.exec()