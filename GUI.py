from pathlib import Path
import os

import programLogic

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt, QProcess, QThread,Signal,Slot
from PySide6.QtGui import QAction, QFont, QCursor
from PySide6.QtWidgets import (QApplication, QDialog, QDialogButtonBox, QGridLayout, QLabel, QLineEdit,
                               QListWidget, QProgressBar, QPushButton, QTreeWidget, QTreeWidgetItem, QFileDialog,QTextBrowser)

# Step 1: Create a Worker class inheriting from QThread
class Worker(QThread):
    # Signal to notify when the task is done (optional, if you want to update the UI)
    finished = Signal()
    update = Signal(str)
    progress = Signal(int)
    

    def __init__(self, ownedPacks, stepsToDo, modsToDownload, userFiles, gameFiles, originalVRAM):
        super().__init__()
        self.ownedPacks = ownedPacks
        self.stepsToDo = stepsToDo
        self.modsToDownload = modsToDownload
        self.userFiles = userFiles
        self.gameFiles = gameFiles
        self.originalVRAM = originalVRAM

    def run(self):
        # Call your pipeline logic in this thread
        programLogic.pipeLine(self.ownedPacks, self.stepsToDo, self.modsToDownload, self.userFiles, self.gameFiles, self.originalVRAM,self.progress,self.update)
        # Emit signal when done
        self.finished.emit()


# UI Class to define the layout and components of the window
class Ui_Window(object):

    def getUserFolder(self):
        possibleUserFolders : list = []
        for path in list(Path("~/Documents/Electronic Arts").expanduser().iterdir()):
            if "Sims 3" in path.name:
                possibleUserFolders.append(path)

        if len(possibleUserFolders) == 1:
            userFolder = possibleUserFolders[0]
        
        return str(userFolder)
    
    def smartSelection(self):
        path = self.GameFilesLineEdit.text()
        
        try:
            for dir in os.listdir(path):
                if dir.startswith("EP") or dir.startswith("SP"):
                    self.ownedPacks.add(dir)
        except:
            pass

        with open(f"{path}/Game/Bin/GraphicsRules.sgr","r") as f:
            for line in f.readlines():
                if "seti textureMemory" in line:
                    self.ComponentsDic["Steps"]["Change allocated GPU VRAM"].setText(3,line[26:-1])
                    self.originalVRAM = line[26:-1]
                    break



        for modsInSection in mods.values():
            for name,info in modsInSection.items():
                dependencies = [] if "Dependencies" not in info else info["Dependencies"]  
                if self.ownedPacks.issuperset(dependencies):
                    self.ComponentsDic["Mods"][name].setCheckState(3, Qt.Checked)
                else:
                    self.ComponentsDic["Mods"][name].setCheckState(3, Qt.Unchecked)
                    
                
                
            
    def startPipeline(self):

        stepsToDo = {"Smooth Patch":self.ComponentsDic["Steps"]["Download Smooth Patch"].checkState(3)._value_ == 2,
                     "MaxFPS":self.ComponentsDic["Steps"]["Set FPS Limit"].text(3),
                     "Borderless":self.ComponentsDic["Steps"]["Borderless"].checkState(3)._value_ == 2,
                     "IntelFix":self.ComponentsDic["Steps"]["Intel Fix"].checkState(3)._value_ == 2,
                     "MoreCPU":self.ComponentsDic["Steps"]["Making The Game Use More CPU"].checkState(3)._value_ == 2,
                     "MoreGPU":self.ComponentsDic["Steps"]["Change allocated GPU VRAM"].text(3),
                     "FlushDCBackup":self.ComponentsDic["Steps"]["Flush DCBackup"].checkState(3)._value_ == 2,
                     "Stopping Store Generated Jpgs":self.ComponentsDic["Steps"]["Stopping Store Generated Jpgs"].checkState(3)._value_ == 2}



        modsToDownload = []

        for k,v in self.ComponentsDic["Mods"].items():
            if v.checkState(3)._value_ == 2:
                modsToDownload.append(k)
        
      # Step 3: Create the worker thread and pass the necessary arguments
        self.worker = Worker(self.ownedPacks, stepsToDo, modsToDownload, self.UserFilesLineEdit.text(),self.GameFilesLineEdit.text(),self.originalVRAM)
        self.worker.finished.connect(self.on_pipeline_finished)
        self.worker.progress.connect(self.update_progress_bar)
        self.worker.update.connect(self.on_update)
        # Step 4: Start the worker thread
        self.worker.start()

    def on_pipeline_finished(self):
        # Code to execute when the pipeline finishes (e.g., update UI or show a message)
        print("Pipeline finished")

    def update_progress_bar(self, value):
        print("Progress",value)
        self.progressBar.setValue(value)
    
    def on_update(self,text : str):
        print("Update", text)
        self.SystemOutput.append(str(text))

    def setupUi(self, Window):
        Window.setObjectName("Window")
        Window.resize(1200, 800)

        self.ownedPacks = set()
        # Create an action (can be connected to functionality later)
        self.actionTeste = QAction(Window)
        self.actionTeste.setCheckable(True)
        self.actionTeste.setObjectName("actionTeste")

        # Set up the grid layout
        self.gridLayout = QGridLayout(Window)
        self.gridLayout.setObjectName("gridLayout")

        # Add file browsing components (labels, buttons, and line edits)
        self.setupFileBrowserComponents(Window)

        # Add progress bar
        self.progressBar = QProgressBar(Window)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setValue(0)
        self.gridLayout.addWidget(self.progressBar, 4, 0, 1, 2)

        # Add System Output label and list widget
        self.SystemOutputLabel = QLabel("System Output", Window)
        self.gridLayout.addWidget(self.SystemOutputLabel, 2, 0)
        self.SystemOutput = QTextBrowser(Window)
        self.SystemOutput.setObjectName("SystemOutput")
        self.gridLayout.addWidget(self.SystemOutput, 3, 0, 1, 2)

        # Add a tree widget for components
        self.Components = QTreeWidget(Window)
        self.Components.setObjectName("Components")
        self.Components.setColumnCount(4)
        self.Components.setHeaderLabels(["Name", "Description", "Dependencies", "Value"])
        self.Components.setColumnWidth(0,370)
        self.Components.setColumnWidth(1,600)
        self.gridLayout.addWidget(self.Components, 1, 0, 1, 2)
        self.ComponentsDic = {}

        # Populate the tree widget with items
        self.addComponents()

        # Add dialog buttons (OK, Cancel, Yes to All, No to All)
        self.DialogButtonBox = QDialogButtonBox(Window)
        self.DialogButtonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel) #| QDialogButtonBox.YesToAll | QDialogButtonBox.NoToAll)
        self.gridLayout.addWidget(self.DialogButtonBox, 9, 0, 1, 2)

        # Connect OK/Cancel buttons to accept/reject methods
        self.DialogButtonBox.accepted.connect(self.startPipeline)
        self.DialogButtonBox.rejected.connect(Window.reject)
        #self.DialogButtonBox.button(QDialogButtonBox.YesToAll).clicked.connect(self.yesToAll)

        # Retranslate and set window title
        self.retranslateUi(Window)

        # Connect UI components to their signals
        QMetaObject.connectSlotsByName(Window)

    def retranslateUi(self, Window):
        Window.setWindowTitle(QCoreApplication.translate("Window", "Sims 3 Performance Fixes Assistant", None))
        self.actionTeste.setText(QCoreApplication.translate("Window", "Test Action", None))

    def yesToAll(self):
        for section in self.ComponentsDic.values():
            for element in section.values():
                if element.checkState(3)._value_ in [0,2]:
                    element.setCheckState(3, Qt.Checked)

        

    def setupFileBrowserComponents(self, Window):
        """Sets up labels, buttons, and line edits for file browsing."""
        # Game Files
        self.GameFilesLabel = QLabel("Game Files", Window)
        self.gridLayout.addWidget(self.GameFilesLabel, 5, 0)
        self.GameFilesLineEdit = QLineEdit(Window)
        self.gridLayout.addWidget(self.GameFilesLineEdit, 6, 0)
        self.GameFilesButton = QPushButton("Browse", Window)
        self.GameFilesButton.clicked.connect(self.browsefilesGame)
        self.gridLayout.addWidget(self.GameFilesButton, 6, 1)

        # User Files
        self.UserFilesLabel = QLabel("User Files", Window)
        self.gridLayout.addWidget(self.UserFilesLabel, 7, 0)
        self.UserFilesLineEdit = QLineEdit(Window)
        self.UserFilesLineEdit.setText(self.getUserFolder())
        self.gridLayout.addWidget(self.UserFilesLineEdit, 8, 0)
        self.UserFilesButton = QPushButton("Browse", Window)
        self.UserFilesButton.clicked.connect(self.browsefilesUser)
        self.gridLayout.addWidget(self.UserFilesButton, 8, 1)


    def browsefilesUser(self):
        fname=QFileDialog.getExistingDirectory(self, 'Open folder', 'C:\\')
        self.UserFilesLineEdit.setText(fname)

    def browsefilesGame(self):
        fname=QFileDialog.getExistingDirectory(self, 'Open folder', 'C:\\')
        self.GameFilesLineEdit.setText(fname)
        self.smartSelection()

    def addComponents(self):

        self.ComponentsDic["Steps"] = {}

        for section, stepsInSection in steps.items():
            parentItem = QTreeWidgetItem(self.Components)
            parentItem.setExpanded(True)
            parentItem.setText(0, section)
            for key in stepsInSection:
                if "Description" == key:
                    parentItem.setText(1, stepsInSection["Description"])
                elif "value" == key:
                    if stepsInSection[key] == "bool":
                        parentItem.setCheckState(3, Qt.Unchecked)
                    else:
                        parentItem.setText(3, stepsInSection[key]) 
                        parentItem.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsDragEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled)
                else:
                        info = stepsInSection[key]
                        # Add child items
                        childItem1 = QTreeWidgetItem(parentItem)
                        childItem1.setExpanded(True)
                        childItem1.setText(0, key)
                        childItem1.setText(1, info["Description"]if "Description" in info else "")
                        childItem1.setText(2, ", ".join(info["Dependencies"] if "Dependencies" in info else ""))
                        if info["value"] == "bool":
                            childItem1.setCheckState(3, Qt.Unchecked)
                        else:
                            childItem1.setText(3, info["value"]) 
                            childItem1.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsDragEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled)
                            
                        self.ComponentsDic["Steps"][key] = childItem1
            
            self.ComponentsDic["Steps"][section] = parentItem 
                    
            
            
        self.ComponentsDic["Mods"] = {}
        for section,modsInSection in mods.items():
            # Create a parent item in the tree widget
            parentItem = QTreeWidgetItem(self.Components)
            parentItem.setExpanded(True)
            parentItem.setText(0, section)
            parentItem.setCheckState(0, Qt.Unchecked)

            for name,info in modsInSection.items():
                # Add child items
                childItem1 = QTreeWidgetItem(parentItem)
                childItem1.setExpanded(True)
                childItem1.setText(0, name)
                childItem1.setText(1, info["Description"]if "Description" in info else "")
                childItem1.setText(2, ", ".join(info["Dependencies"] if "Dependencies" in info else ""))
                childItem1.setCheckState(3, Qt.Unchecked)
                self.ComponentsDic["Mods"][name] = childItem1

# Main window class inheriting from QDialog and Ui_Window
class MyWindow(QDialog, Ui_Window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

# Main entry point for the application
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    import json

    with open("mods.json","r") as f:
        mods = json.load(f)

    with open("steps.json","r") as f:
        steps = json.load(f)

    # Create and show the window
    window = MyWindow()
    window.show()
    
    # Execute the application
    sys.exit(app.exec())
