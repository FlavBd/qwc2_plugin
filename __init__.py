#-----------------------------------------------------------
# Copyright (C)
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

from PyQt5.QtWidgets import QAction, QMessageBox, QDialog, QApplication, QWidget, QPushButton, QLabel, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt
#from .resources import *
from qgis.core import QgsProject

def classFactory(iface):
     return AddNewProject(iface)

class AddNewProject:
    def __init__(self, iface):
         self.iface = iface
         self.dialog = QDialog(iface.mainWindow())
         self.dialog.setGeometry(320,200,500,300)
         
         #Labels
         self.labeltitle = QLabel('Ajouter un nouveau projet à mon application QWC2', self.dialog)
         self.labeltitle.move(70,10)
         self.labelserver = QLabel('Serveur :', self.dialog)
         self.labelserver.move(10,50)
         self.labeluser = QLabel('Utilisateur :', self.dialog)
         self.labeluser.move(10,100)
         self.labelpassword = QLabel('Mot de passe :', self.dialog)
         self.labelpassword.move(10,150)

         #zone de remplissage
         self.editserver = QLineEdit("", self.dialog)
         self.editserver.move(100,50)
         self.edituser = QLineEdit("", self.dialog)
         self.edituser.move(100,100)
         self.editpassword = QLineEdit("", self.dialog)
         self.editpassword.setEchoMode(QLineEdit.Password)
         self.editpassword.move(100,150)

         #Bouton de validation
         self.button = QPushButton('Ajouter le projet à mon application', self.dialog)
         self.button.setToolTip('Cliquer ici pour ajouter le projet')
         self.button.move(250,200)
         self.button.clicked.connect(self.confirm_button)
 
    def confirm_button(self):
         #Récupérer les données entrées dans les zones de texte
         self.server = self.editserver.text()
         self.user = self.edituser.text()
         self.password = self.editpassword.text()
         #Afficher les informations pour confirmation
         self.buttoncheck = QMessageBox.question(None, 'Confirmer les informations', "serveur : " + self.server + "   utilisateur : " + self.user + "   mot de passe : " + self.password, QMessageBox.Ok, QMessageBox.Cancel)
         if self.buttoncheck == QMessageBox.Ok:
              self.project = QgsProject.instance().fileName()
              #Projet enregistré / ouvert ?
              if self.project == "":
                   self.projectname = QMessageBox.question(None, 'Information sur le projet', "Aucun projet ouvert ou le projet en cours n'est pas enregistré", QMessageBox.Ok, QMessageBox.Cancel)
              else:
                   #Est ce bien un .qgs ?
                   if self.project.endswith(".qgs"):
                        self.projectname = QMessageBox.question(None, 'Information sur le projet', "nom du projet : " + self.project, QMessageBox.Ok, QMessageBox.Cancel)
                   else:
                        self.projectname = QMessageBox.question(None, 'Information sur le projet', "L'extension du fichier n'est pas la bonne : " + self.project + "  merci d'enregistrer le projet en .qgs", QMessageBox.Ok, QMessageBox.Cancel)


                   #QGIS Server coché ?
                   #Symboles
                   #Exécution script


    def initGui(self):
         self.action = QAction(QIcon(":/plugins/AddNewProject/qwc2.png"), "Add new project in QWC2",
                              self.iface.mainWindow())
         #self.action = QAction('Hello!', self.iface.mainWindow())
         self.action.triggered.connect(self.run)
         self.iface.addToolBarIcon(self.action)

    def unload(self):
         self.iface.removePluginMenu("Add new project in QWC2",
                                    self.action)
         self.iface.removeToolBarIcon(self.action)
         del self.action

    def run(self):
         self.dialog.exec()