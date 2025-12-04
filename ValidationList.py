from PySide2 import QtWidgets, QtGui, QtCore
import maya.cmds as mc


class ValidationList(QtWidgets.QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self._isValid = True
        
        self.buildUI()
    
    def buildUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
                
        self.labelLayout = QtWidgets.QVBoxLayout()
        self.labelLayout.setContentsMargins(0, 0, 0, 0)
        self.labelLayout.setSpacing(2)
        
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.font.setPointSize(10)
        
        self.label = QtWidgets.QLabel(f"{self.title}: ")
        self.label.setFont(self.font)
        
        self.field = QtWidgets.QListWidget()
        self.field.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
            
        self.labelLayout.addWidget(self.label)
        self.labelLayout.addWidget(self.field)
        
        self.layout.addLayout(self.labelLayout)
    
    def addItem(self, itemName, validationList=None):
        listItem = QtWidgets.QListWidgetItem(itemName)
        
        if validationList:
            if itemName in validationList:
                listItem.setBackgroundColor(QtGui.QColor("#4fa000"))
            else:
                listItem.setBackgroundColor(QtGui.QColor("#ba484e"))
                self._isValid = False
        else:
            if mc.objExists(itemName):
                listItem.setBackgroundColor(QtGui.QColor("#4fa000"))
            else:
                listItem.setBackgroundColor(QtGui.QColor("#ba484e"))
                self._isValid = False
        
        self.field.addItem(listItem)
    
    def isValid(self):
        return self._isValid