'''
    ImageQuizzerModuleConnector utility for Baines Image Quizzer.

    Application to update the NA-MIC Extensions Slicer-xxxx.ini file with the path to the 
    Baines Image Quizzer. Additionally, there is a button to start the Image Quizzer.

    This utility makes a USB more portable for the user. The user does not need to know 
    how to manually add the module path to this list.  The update of the Slicer-xxxx.ini file uses
    the current drive letter for the USB which can change depending which PC or laptop the USB is plugged into.

    This source file is packaged into a static executable using 'pyinstaller' . 
    The resulting executable is added to the BainesImageQuizzer project.
    
    Author: Carol Johnson (Baines Imaging Research Laboratories - LRCP London, ON)
    Date:   February 2024
    
    Packaging:  >> cd to dir containing this module
                >> pyinstaller ImageQuizzerInstaller.py --noconsole -n "USB-ConnectAndStartImageQuizzer" --onefile
                >> copy ./dist/USB-ConnectAndStartImageQuizzer.exe to BainesImageQuizzer project folder

    Usage:      >> ****

    Documentation: https://baines-imaging-research-laboratory.github.io/ImageQuizzerDocumentation
'''

from PyQt5 import QtWidgets

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtGui


import sys, os
from pathlib import Path
import traceback
import re
import fileinput


##########################################################################
#
# ImageQuizzerModuleConnector
#
##########################################################################
class ImageQuizzerModuleConnector(QMainWindow):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, *args, **kwargs):
        super(ImageQuizzerModuleConnector, self).__init__(*args, **kwargs)

        # self.setGeometry(300,300,300,300)
        self.setWindowTitle("USB Support - Starting Image Quizzer")
        self.setFixedWidth(500)

        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)

        self.oFormWidget = FormWidget(self)
        self.setCentralWidget(self.oFormWidget)


##########################################################################
#
# FormWidget
#
##########################################################################
class FormWidget(QWidget):
    ''' Setup GUI for install application
    '''

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, parent):
        super(FormWidget, self).__init__(parent)

        self.statusBar = self.parent().statusBar
        self.sImageQuizzerDir = None
        self.sSlicerDir  = None


        self.sCurrentDirectory = os.getcwd()
        self.sDefaultModulePath = os.path.join(os.path.dirname(self.sCurrentDirectory),'BainesImageQuizzer')

        self.qMainLayout = QtWidgets.QGridLayout()

        qLblInfo = QtWidgets.QLabel()
        qLblInfo.setWordWrap(True)
        qLblInfo.setText("This application will update Slicer's module list and start the Image Quizzer module."\
                         + " Use the 'Connect' button when plugging a USB into different PCs.\n")

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Image Quizzer location

        qLblModuleLocation = QtWidgets.QLabel("Image Quizzer location:")

        self.qLineModulePath = QtWidgets.QLineEdit()
        self.qLineModulePath.setText(self.sDefaultModulePath)
        
        qBtnChangeModulePath = QtWidgets.QPushButton("Browse")
        qBtnChangeModulePath.clicked.connect(self.getModuleLocationPath)

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Slicer location

        qLblSlicerLocation = QtWidgets.QLabel("Slicer location :")
        self.qLineSlicerPath = QtWidgets.QLineEdit(os.path.dirname(self.sCurrentDirectory))

        qBtnChangeSlicerPath = QtWidgets.QPushButton("Browse")
        qBtnChangeSlicerPath.clicked.connect(self.getSlicerLocationPath)

        qLblInstructions = QtWidgets.QLabel("\nConnect module to Slicer (first time or when changing PCs) and Start\n")
        qBtnConnectSlicer = QtWidgets.QPushButton("Connect")
        qBtnConnectSlicer.clicked.connect(self.setupConnectModule)

        qBtnStartSlicer = QtWidgets.QPushButton("Start")
        qBtnStartSlicer.clicked.connect(self.startSlicer)
                                    

         
        # add widgets to layout
        self.qMainLayout.addWidget(qLblInfo,0,0)
        self.qMainLayout.addWidget(qLblModuleLocation,1,0)
        self.qMainLayout.addWidget(self.qLineModulePath,2,0)
        self.qMainLayout.addWidget(qBtnChangeModulePath,2,1)

        self.qMainLayout.addWidget(qLblSlicerLocation,3,0)
        self.qMainLayout.addWidget(self.qLineSlicerPath,4,0)
        self.qMainLayout.addWidget(qBtnChangeSlicerPath,4,1)

        self.qMainLayout.addWidget(qLblInstructions,5,0)
        self.qMainLayout.addWidget(qBtnConnectSlicer,6,0)
        self.qMainLayout.addWidget(qBtnStartSlicer,7,0)

 
        self.setLayout(self.qMainLayout)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getModuleLocationPath(self):

        self.statusBar.showMessage("")
        if self.sImageQuizzerDir == None:
            sDisplayDir = os.path.dirname(self.sCurrentDirectory)
        else:
            sDisplayDir = os.path.dirname(self.sImageQuizzerDir)
        
        qDialog = QtWidgets.QFileDialog()
        self.sImageQuizzerDir = qDialog.getExistingDirectory(self,\
                                                "Select installation folder",\
                                                sDisplayDir,\
                                                QtWidgets.QFileDialog.ShowDirsOnly)
        
        if self.sImageQuizzerDir == '':  # cancelled
            self.qLineModulePath.setText(self.sDefaultModulePath)
        else:
            self.qLineModulePath.setText(self.sImageQuizzerDir)
            

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getSlicerLocationPath(self):

        self.statusBar.showMessage("")
        if self.sSlicerDir == None:
            sDisplayDir = os.path.dirname(self.sCurrentDirectory)
        else:
            sDisplayDir = os.path.dirname(self.sSlicerDir)
        
        qDialog = QtWidgets.QFileDialog()
        self.sSlicerDir = qDialog.getExistingDirectory(self,\
                                                "Select Slicer installation folder",\
                                                sDisplayDir,\
                                                QtWidgets.QFileDialog.ShowDirsOnly)
        
        if self.sSlicerDir == '':  # cancelled
            self.qLineSlicerPath.setText(os.path.dirname(self.sCurrentDirectory))
        else:
            self.qLineSlicerPath.setText(self.sSlicerDir)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setupConnectModule(self):
        ''' This function checks that the Slicer extensions have already been installed (manual operation).
            Then the Slicer.ini file is modified to add the Image Quizzer to the list of modules.
        '''
        self.statusBar.showMessage("")

        oAppLogic = ApplicationLogic(self.statusBar)
        oAppLogic.connectModuleInSlicer( self.qLineModulePath.text(), self.qLineSlicerPath.text())
           
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def startSlicer(self):
        pass
       

##########################################################################
#
# ApplicationLogic
#
##########################################################################
class ApplicationLogic():

    def __init__(self,qStBar):
        self.statusBar = qStBar


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def connectModuleInSlicer(self, sModulePath, sSlicerPath):
        ''' Function to add ImageQuizzer module path to Slicer's list of modules 
            in the Application Settings.

            At the time of writing, the ini file is named Slicer-29738.ini .
            This function is setup to make this name generic in case of future upgrades.

            This ini file is created when the administrator manually connects a module
            in Slicer's application settings or when extensions are added. 

            This function looks for a previous connection to the module's code path
            and if it exists it may have the wrong path.
            It will be removed from the line and new path will be appended to end of line.

        '''
        try:
            #check that ini file exists
            bFileFound = False
            bModuleUpdated = False
            sMsg = ''

            sSearchDir = os.path.join(sSlicerPath,'NA-MIC')
            if os.path.exists(sSearchDir):
                
                lFiles = os.listdir(sSearchDir)
                for sFile in lFiles:
                    if re.match("^Slicer.*ini$",sFile):
                        bFileFound = True
                        break

            if bFileFound == False:
                qMsgBox = QtWidgets.QMessageBox()
                qMsgBox.setWindowTitle("ERROR!!!")
                qMsgBox.setText("Cannot connect Image Quizzer module to Slicer. Either: ")
                qMsgBox.setInformativeText('\n   -the location specified for Slicer is incorrect OR'\
                                        '\n   -the required Slicer Extensions have not yet been installed. (Slicer-xxxx.ini file is missing)'\
                                        +'\n\nSee documentation > Getting started'\
                                            +'\nhttps://baines-imaging-research-laboratory.github.io/ImageQuizzerDocumentation')
                qMsgBox.exec() 
                return
            
            else:

                # file found - update Modules list
                self.statusBar.showMessage("Updating modules lists " + sFile)
                sSlicerIniPath = os.path.join(sSearchDir, sFile)
                sImageQuizzerCodePath = os.path.join(sModulePath,'ImageQuizzer','Code').replace('\\','/')

                if os.path.exists(sImageQuizzerCodePath):

                    sLineToFind = "AdditionalPaths="
                    sSubstringToFind = "ImageQuizzer/Code"
        
                    for line in fileinput.FileInput(sSlicerIniPath, inplace=True):
                        if sLineToFind in line:

                            #remove any existing entries
                            indSearchStart = 0
                            while(indSearchStart < len(line)):
                                iLengthLine = len(line) # for debug
                                if sSubstringToFind in line:

                                    iStartIndSubstr = line.find(sSubstringToFind, indSearchStart)
                                    if iStartIndSubstr > -1:
                                        iEndIndSubstr = iStartIndSubstr + len(sSubstringToFind)

                                        #end of line entry
                                        if iEndIndSubstr == len(line) -1: # entry at end of line (\n included in length)
                                            iStartIndOfRemoval = line.rfind(',',0,iStartIndSubstr)

                                            if iStartIndOfRemoval == -1: # no preceding comma - must be the first
                                                iStartIndOfRemoval = line.rfind('=',0,iStartIndSubstr)
                                                line = line[0 : iStartIndOfRemoval + 1] + line[iEndIndSubstr :]

                                            else:
                                                line = line[0 : iStartIndOfRemoval] + line[iEndIndSubstr :]

                                            indSearchStart = len(line)

                                        # not end of line entry
                                        else: # check if part of longer path
                                            if line[iEndIndSubstr] == '/':
                                                indSearchStart = iEndIndSubstr + 1

                                            else: # correct entry
                                                iStartIndOfRemoval = line.rfind(',',0,iStartIndSubstr)
                                                if iStartIndOfRemoval == -1: # no preceding comma - must be the first
                                                    iStartIndOfRemoval = line.rfind('=',0,iStartIndSubstr)
                                                    line = line[0 : iStartIndOfRemoval + 1] + line[iEndIndSubstr + 1 : ]
                                                    indSearchStart = iStartIndOfRemoval + 1
                                                else:
                                                    line = line[0 : iStartIndOfRemoval] + line[iEndIndSubstr + 1 : ]
                                                    indSearchStart = iStartIndOfRemoval

                                    else: # not found in (remainder of) search
                                        indSearchStart = len(line) # end the while loop

                                else:   # not found
                                    indSearchStart = len(line) # end the while loop



                            # append to end of line
                            line = line.rstrip('\n')
                            if len(line) == len(sLineToFind):
                                line = line + sImageQuizzerCodePath + '\n'
                            else:
                                line = line + ', ' + sImageQuizzerCodePath + '\n'

                            bModuleUpdated = True

                        print(line, end='')


                    fileinput.close()
                    if bModuleUpdated:
                        self.statusBar.showMessage('Slicer module list updated')
                    else: 
                        sMsg = "Problem with Slicer-xxxx.ini file. Add module manually in Slicer's Applications>Modules settings or see administrator."
                        raise

                else:
                    sMsg = "..\\ImageQuizzer\\Code folder is missing. " + \
                            "Reset the Image Quizzer location above to the installation directory."
                    raise

        except:
            tb = traceback.format_exc()
            sMsg = sMsg + '\n' + tb
            self.statusBar.showMessage('ERROR Connecting module to Slicer')
            qMsgBox = QtWidgets.QMessageBox()
            qMsgBox.setWindowTitle("ERROR!!!")
            qMsgBox.setText("Cannot connect Image Quizzer module to Slicer")
            qMsgBox.setInformativeText(sMsg)
            qMsgBox.exec() 
                                           

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



##########################################################################
##########################################################################
##########################################################################
#
# RUN APPLICATION
#
##########################################################################
##########################################################################
##########################################################################


if __name__ == '__main__':

    app=QApplication(sys.argv)

    IQModuleConnector = ImageQuizzerModuleConnector()
    IQModuleConnector.show()

    app.exec()
