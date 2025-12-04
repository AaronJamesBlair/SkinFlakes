from PySide2 import QtWidgets, QtGui, QtCore
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from SkinFlakes import ValidationWidget
from SkinFlakes import imagePath

from importlib import reload
reload(ValidationWidget)


class SkinFlakes(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    appName = "SkinFlakes"
    
    def __init__(self):
        super().__init__()
        self.skinData = None
        self.filePath = None
        
        self.setWindowTitle(self.appName)
        
        self.buildUI()
        self.buildMenu()
        self.buildConnections()
        
    def buildUI(self):        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.menuBar = QtWidgets.QMenuBar(self)
        
        self.tabWidget = QtWidgets.QTabWidget()
        
        self.applyButton = QtWidgets.QPushButton("Apply SkinFlakes")
        self.applyButton.setEnabled(False)
        
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setRange(0, 1)
        self.progressBar.setVisible(False)
        
        self.layout.addWidget(self.menuBar)
        self.layout.addWidget(self.tabWidget)
        self.layout.addWidget(self.applyButton)
        self.layout.addWidget(self.progressBar)
    
    def buildMenu(self):
        self.fileMenu = self.menuBar.addMenu("File")
        
        self.loadAction = self.fileMenu.addAction("Load SkinFlakes")
        self.exportAction = self.fileMenu.addAction("Export SkinFlakes")
        
        self.refreshAction = self.menuBar.addAction("Refresh")
    
    def buildConnections(self):
        self.loadAction.triggered.connect(self.loadSkinFlakes)
        self.applyButton.clicked.connect(self.applySkinFlakes)
        self.exportAction.triggered.connect(self.exportSkinFlakes)

        self.refreshAction.triggered.connect(self.refresh)
    
    def refresh(self):
        if self.filePath:
            self._loadSkinFlakes(self.filePath)
    
    def loadSkinFlakes(self):
        self.filePath = QtWidgets.QFileDialog().getOpenFileName(self, "Select skinFlakes file", "", "skinFlakes (*.skinFlakes)")[0]
        
        if self.filePath:
            self._loadSkinFlakes(self.filePath)
    
    def _loadSkinFlakes(self, filePath):
        self.clear()
        with open(filePath, "r") as jsonFile:
            self.skinData = json.load(jsonFile)
        
        allValid = True
        for num, skinCluster in enumerate(self.skinData):
            validationWidget = ValidationWidget.ValidationWidget()
            validationWidget.populate(skinCluster, self.skinData[skinCluster])
            
            index = self.tabWidget.addTab(validationWidget, skinCluster)
            
            if validationWidget.isValid():
                self.tabWidget.setTabIcon(index, QtGui.QIcon(imagePath + "valid.png"))
            else:
                self.tabWidget.setTabIcon(index, QtGui.QIcon(imagePath + "invalid.png"))
                allValid = False
        
        if allValid:
            self.applyButton.setEnabled(True)
        else:
            self.applyButton.setEnabled(False)
            
        self.setWindowTitle(self.appName + f" - {filePath}")
    
    def clear(self):
        count = self.tabWidget.count()
        
        for i in range(count, -1, -1):
            self.tabWidget.removeTab(i)
    
    def applySkinFlakes(self):
        if self.skinData:
            self.progressBar.setVisible(True)
            
            vertCount = 0
            for skin in self.skinData:
                vertCount += len(list(self.skinData[skin]["values"].keys()))
            
            self.progressBar.setValue(0)
            self.progressBar.setRange(0, vertCount)
            
            # Want to cull out missing joints from skin so we don't get errors
            count = 0
            for skin in self.skinData:
                components = self.skinData[skin]["components"]
                for vert in self.skinData[skin]["values"]:        
                    jointList = []
                    for component in self.skinData[skin]["values"][vert]:
                        componentName = list(component.keys())[0]
                        value = component[componentName]
                        jointList.append([componentName, value])
                        
                    mc.select(vert)
                    
                    try:
                        mc.skinPercent(skin, tv=jointList)
                    except Exception as e:
                        print(e)
                        
                    self.progressBar.setValue(count+1)
                    count += 1
            
            self.progressBar.setVisible(False)
    
    def exportSkinFlakes(self):
        filePath = QtWidgets.QFileDialog().getSaveFileName(self, "Select Export Location...", "", "skinFlakes (*.skinFlakes)")[0]
        
        if filePath:
            self.progressBar.setVisible(True)
            
            sel = mc.ls(sl=True)
            skinData = {}
            for item in sel:
                allVerts = cmds.ls(f'{item}.vtx[*]', flatten=True)
                self.progressBar.setRange(0, len(allVerts))
                self.progressBar.setValue(0)
                
                history = cmds.listHistory(item)
                skins = mc.ls(history, type="skinCluster")
                
                for skin in skins:
                    components = mc.skinCluster(skin, q=True, inf=True)
                    skinData[skin] = {"components": components, "values": {}, "meshes": [item]}
                    
                    for vertNum, vert in enumerate(allVerts):
                        skinData[skin]["values"][vert] = []
                    
                        value = mc.skinPercent(skin, vert, q=True, v=True)            
                        for num, item in enumerate(value):
                            componentName = components[num]
                            if "|" in componentName:
                                componentName = componentName.split("|")[-1]
                                
                            skinData[skin]["values"][vert].append({componentName: item})
                        
                        self.progressBar.setValue(vertNum+1)

            with open(filePath, "w") as jsonFile:
                jsonFile.write(json.dumps(skinData, indent=4))
        
            self.progressBar.setVisible(False)
            
        
if __name__ == "__main__":
    s = SkinFlakes()
    s.show()