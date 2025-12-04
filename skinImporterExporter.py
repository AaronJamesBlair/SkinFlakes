from PySide2 import QtWidgets, QtGui, QtCore
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


class SkinImporterExporter(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SkinImporterExporter")

        self.buildUI()
        self.buildConnections()
    
    def buildUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.exportButton = QtWidgets.QPushButton("Export Skin Weights")
        self.importButton = QtWidgets.QPushButton("Import Skin Weights")
        
        self.exportButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.importButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setRange(0, 1)

        self.buttonLayout.addWidget(self.importButton)
        self.buttonLayout.addWidget(self.exportButton)
        
        self.layout.addLayout(self.buttonLayout)
        self.layout.addWidget(self.progressBar)
    
    def buildConnections(self):     
        self.exportButton.clicked.connect(self.exportSkinWeights)
        self.importButton.clicked.connect(self.importSkinWeights)

    def exportSkinWeights(self):
        filePath = QtWidgets.QFileDialog().getSaveFileName(self, "Select Export Location...", "", "skinFlakes (*.skinFlakes)")[0]
        
        if filePath:
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

    def importSkinWeights(self):
        filePath = QtWidgets.QFileDialog().getOpenFileName(self, "Select skinFlakes file", "", "skinFlakes (*.skinFlakes)")[0]
        
        if filePath:
            with open(filePath, "r") as jsonFile:
                skinData = json.load(jsonFile)
            
            vertCount = 0
            for skin in skinData:
                vertCount += len(list(skinData[skin]["values"].keys()))
            
            self.progressBar.setValue(0)
            self.progressBar.setRange(0, vertCount)
            
            
            # Want to cull out missing joints from skin so we don't get errors
            count = 0
            for skin in skinData:
                components = skinData[skin]["components"]
                for vert in skinData[skin]["values"]:        
                    jointList = []
                    for component in skinData[skin]["values"][vert]:
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
                    

if __name__ == "__main__":
    s = SkinImporterExporter()
    s.show()