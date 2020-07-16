import os
from qgis.PyQt.QtWidgets import QWidget, QCheckBox
from qgis.PyQt import uic

class ProjectWidget(QWidget):
    def __init__(self, item, backgrounds, parent=None):
        super(ProjectWidget, self).__init__(parent)
        print("here")
        uic.loadUi(os.path.join(os.path.dirname(__file__), "project_dialog.ui"), self)
        print("there")
        self.__item = item
        print(item['scales'])
        self.scaleLineEdit.setText(str([int(s) for s in item['scales']])[1:-1])

        defaultBackgroundIdx = None
        self.backgroundComboBox.addItem("")
        for i, layer in enumerate(backgrounds):
            self.backgroundComboBox.addItem(layer['name'])
            checkBox = QCheckBox(layer['name'])
            self.backgroundLayout.addWidget(checkBox)
            for l in item['backgroundLayers']:
                if (l['name']==layer['name']) == 1:
                    checkBox.setChecked(True)
                    if l['visibility']:
                        defaultBackgroundIdx = i + 1

        if defaultBackgroundIdx is not None:
            self.backgroundComboBox.setCurrentIndex(defaultBackgroundIdx)

        if 'coordinates' in item['searchProviders']:
            self.coordinatesCheckBox.setChecked(True)
        if 'nominatim' in item['searchProviders']:
            self.nominatimCheckBox.setChecked(True)

    def item(self):

        self.__item['scales'] = self.scaleLineEdit.text().split(',')
        checkBoxes = [self.backgroundLayout.itemAt(i).widget() 
            for i in range(self.backgroundLayout.count())]
        self.__item['backgroundLayers'] = [
            {"name": c.text(),
            "visibility": c.text() == self.backgroundComboBox.currentText(),
            "printLayer": "TODO"
            } 
            for c in checkBoxes if c.isChecked()]
            
        self.__item["searchProviders"] = []
        if self.coordinatesCheckBox.isChecked() == True:
            self.__item["searchProviders"].append("coordinates")
        if self.nominatimCheckBox.isChecked() == True:
            self.__item["searchProviders"].append("nominatim")

        return self.__item