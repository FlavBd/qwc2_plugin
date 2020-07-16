from qgis.PyQt.QtWidgets import QDialog, QWidget, QPushButton, QVBoxLayout
from qgis.PyQt import uic
from qgis.core import QgsSettings
from urllib import request
from subprocess import Popen, check_output, PIPE
# from flask import Flask
import os
import sys

class ConfigDialog(QWidget):
    def __init__(self, currentQgisProjectFile, parent=None):
        super(ConfigDialog, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "config_dialog.ui"), self)
        s = QgsSettings()
        self.urlLineEdit.setText(s.value("qwc2configurator/server/url",""))
        self.usernameLineEdit.setText(s.value("qwc2configurator/server/username",""))
        self.passwordLineEdit.setText(s.value("qwc2configurator/server/password",""))
        self.currentQgisProjectFile = currentQgisProjectFile
        if self.currentQgisProjectFile is None or not os.path.isfile(self.currentQgisProjectFile):
            self.publishProjectButton.setEnabled(False)
            self.publishProjectButton.setToolTip("there is no current QGIS project file")
        else:
            self.publishProjectButton.clicked.connect(self.publishProject)
        if self.currentQgisProjectFile is not None and not self.currentQgisProjectFile.endswith(".qgs"):
            self.publishProjectButton.setEnabled(False)
            self.publishProjectButton.setToolTip("the project extension is not .qgs")
        else:
            self.publishProjectButton.clicked.connect(self.publishProject)
    
    def accept(self):
        s = QgsSettings()
        s.setValue("qwc2configurator/server/url", self.urlLineEdit.text())
        s.setValue("qwc2configurator/server/username", self.usernameLineEdit.text())
        s.setValue("qwc2configurator/server/password", self.passwordLineEdit.text())
    
    def publishProject(self):
        self.accept()
        print("on publie")
        s = QgsSettings()
        if self.urlLineEdit.text().endswith("/"):
            self.end = self.urlLineEdit.text()[:-1]
        if self.urlLineEdit.text().startswith("https"):
            self.server = self.end[8:]
            f = request.urlopen(s.value("qwc2configurator/server/url",""))
            print(f.read().decode('utf-8'))
        else: 
            if self.urlLineEdit.text().startswith("http"):
                self.server = self.end[7:]
                f = request.urlopen(s.value("qwc2configurator/server/url",""))
                print(f.read().decode('utf-8'))
            else:
                self.server = self.urlLineEdit.text()

        app.config['SSH_SERVER'] = self.server
        app.config['SSH_USERNAME'] = self.usernameLineEdit.text()
        app.config['SSH_PASSWORD'] = self.passwordLineEdit.text()
        app.config['PROJECT'] = self.currentQgisProjectFile

        #self.script = check_output(["bash", "add_project.sh", self.project, self.server], shell = True)
        # self.script = Popen(['./add_project.sh %s %s' % (self.project, self.server)], stdin=PIPE, stdout=PIPE, stderr = PIPE, shell = True)
        # self.result = ssh.stdout.readlines()
        # if result == []:
        #     error = ssh.stderr.readlines()
        #     print(sys.stderr, "ERROR: %s" % error)
        # else:
        #     print(result)
        # self.script.communicate(self.passwordLineEdit.setText(s.value("qwc2configurator/server/password","")))
        # print(self.script)

if __name__ == "__main__":
    from qgis.core import QgsApplication
    import sys
    a = QgsApplication([], False)
    a.initQgis()
    d = QDialog()
    l = QVBoxLayout()
    d.setLayout(l)
    b = QPushButton("Accept")
    w = ConfigDialog(sys.argv[1] if len(sys.argv) >= 2 else None)
    b.clicked.connect(w.accept)
    l.addWidget(w)
    l.addWidget(b)
    d.show()
    a.exec()