from .config_dialog import ConfigDialog
from qgis.PyQt.QtWidgets import QAction, QDialog, QVBoxLayout, QPushButton
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProject
import os


class Plugin:
    def __init__(self, iface):
        self.iface = iface
          
    def initGui(self):
        self.action =  self.iface.pluginToolBar().addAction(
            QIcon(os.path.join(os.path.dirname(__file__), 'qwc2.png')),
            "open config dialog"
            )
        self.action.triggered.connect(self.openDialog)
    
    def openDialog(self):
        currentQgisProjectFile = QgsProject.instance().fileName()
        if not currentQgisProjectFile or not os.path.isfile(currentQgisProjectFile):
            self.iface.messageBar().pushWarning("Warning", "There is no project file")
            return
        ConfigDialog(currentQgisProjectFile).exec_()

    def unload(self):
        self.iface.pluginToolBar().removeAction(self.action)
