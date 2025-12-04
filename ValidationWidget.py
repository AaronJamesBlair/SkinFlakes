from PySide2 import QtWidgets, QtGui, QtCore
from SkinFlakes import ValidationList
import maya.cmds as mc

from importlib import reload
reload(ValidationList)


class ValidationWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.buildUI()
    
    def buildUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.skinClusterValidationLayout = QtWidgets.QHBoxLayout()
        self.skinClusterValidationLabel = QtWidgets.QLabel("Skin Cluster: ")
        self.skinClusterValidationField = QtWidgets.QLineEdit()
        
        self.skinClusterValidationLayout.addWidget(self.skinClusterValidationLabel)
        self.skinClusterValidationLayout.addWidget(self.skinClusterValidationField)
        
        self.meshValidationList = ValidationList.ValidationList("Meshes")
        self.meshValidationList.field.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.meshValidationList.field.setMaximumHeight(128)
        
        self.jointsValidationList = ValidationList.ValidationList("Joints")
        
        self.layout.addLayout(self.skinClusterValidationLayout)
        self.layout.addWidget(self.meshValidationList)
        self.layout.addWidget(self.jointsValidationList)
        self.layout.addStretch()
    
    def populate(self, skinCluster, skinClusterData):
        self.skinClusterValidationField.setText(skinCluster)
        if mc.objExists(skinCluster):
            style = "background: #4fa000"
        else:
            style = "background: #ba484e"

        self.skinClusterValidationField.setStyleSheet(style)
        
        for mesh in skinClusterData["meshes"]:
            self.meshValidationList.addItem(mesh)
        
        joints = skinClusterData["components"]
        joints.sort()
        
        clusterJoints = []
        if mc.objExists(skinCluster):
            clusterJointsLong = mc.skinCluster(skinCluster, q=True, inf=True)
            
            for joint in clusterJointsLong:
                clusterJoints.append(joint.split("|")[-1])
                
        for joint in joints:
            self.jointsValidationList.addItem(joint, validationList=clusterJoints)
    
    def isValid(self):
        return self.meshValidationList.isValid() and self.jointsValidationList.isValid() and mc.objExists(self.skinClusterValidationField.text())
    