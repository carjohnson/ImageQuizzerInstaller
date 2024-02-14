'''
    Windows installer for Baines Image Quizzer.

    Installation utility to copy files from the current directory to the user specified directory.

    This source file ImageQuizzerInstaller.py is packaged into a static executable using 'pyinstaller' . 
    The resulting executable is added to the BainesImageQuizzer project providing the administrator with
    a simple tool to copy all files in the Baines Image Quizzer project folder into either
    a new location or to replace an existing installation.

    Additionally, if installing to an existing installation, this application will create a backup
    (if requested) of the original module thus preserving the current input settings and output files.
    
    
    Author: Carol Johnson (Baines Imaging Research Laboratories - LRCP London, ON)
    Date:   February 2024
    
    Packaging:  >> cd to dir containing this module
                >> pyinstaller ImageQuizzerInstaller.py --noconsole -n "setup-win" --onefile
                >> copy ./dist/setup-win.exe to BainesImageQuizzer project folder

    Usage:      >> cd to download of BainesImageQuizzer project
                >> setup-win
'''

from PyQt5 import QtWidgets

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtGui


import sys, os
from pathlib import Path
from datetime import datetime
import shutil
import traceback


##########################################################################
#
# ImageQuizzerInstallerWindow
#
##########################################################################
class ImageQuizzerInstallerWindow(QMainWindow):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, *args, **kwargs):
        super(ImageQuizzerInstallerWindow, self).__init__(*args, **kwargs)

        # self.setGeometry(300,300,300,300)
        self.setWindowTitle("Setup Baines Image Quizzer")
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
        self.sInstallDir = None


        self.sCurrentDirectory = os.getcwd()
        sDefaultInstallDirectory = os.path.join(os.path.dirname(self.sCurrentDirectory),'BainesImageQuizzer')

        self.qMainLayout = QtWidgets.QGridLayout()

        qLblInfo = QtWidgets.QLabel()
        qLblInfo.setWordWrap(True)
        qLblInfo.setText("This application will install the Baines Image Quizzer at the specified destination, " +\
                         "replacing any pre-existing module. Additionally, it will create a backup" +\
                        " if requested in order to preserve any input settings and output results.\n")

        qLblInstallPath=QtWidgets.QLabel()
        qLblInstallPath.setText("Install path :")

        self.qInstallPath = QtWidgets.QLineEdit()
        self.qInstallPath.setText(sDefaultInstallDirectory)
        
        qBtnChangePath = QtWidgets.QPushButton("Change")
        qBtnChangePath.setCheckable(True)
        qBtnChangePath.clicked.connect(lambda:self.getNewInstallPath(self.sCurrentDirectory))


        qBtnInstall = QtWidgets.QPushButton("Install")
        qBtnInstall.setCheckable(True)
        qBtnInstall.clicked.connect(self.setupInstall)


         
        # add widgets to layout
        self.qMainLayout.addWidget(qLblInfo,0,0)
        self.qMainLayout.addWidget(qLblInstallPath,1,0)
        self.qMainLayout.addWidget(self.qInstallPath,2,0)
        self.qMainLayout.addWidget(qBtnChangePath,2,1)
        self.qMainLayout.addWidget(qBtnInstall,3,1)
 
        self.setLayout(self.qMainLayout)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getNewInstallPath(self, sCurrentDirectory):

        self.statusBar.showMessage("")
        if self.sInstallDir == None:
            sDisplayDir = sCurrentDirectory
        else:
            sDisplayDir = os.path.dirname(self.sInstallDir)
        
        qDialog = QtWidgets.QFileDialog()
        self.sInstallDir = qDialog.getExistingDirectory(self,\
                                                "Select installation folder",\
                                                sDisplayDir,\
                                                QtWidgets.QFileDialog.ShowDirsOnly)
        
        if self.sInstallDir == '':  # cancelled
            self.qInstallPath.setText(sDisplayDir)
        else:
            self.qInstallPath.setText(self.sInstallDir)
            

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setupInstall(self):

        self.statusBar.showMessage("")
        oInstallLogic = InstallerLogic()
        oInstallLogic.installSoftware(self.sCurrentDirectory, self.qInstallPath.text(), self.statusBar)


##########################################################################
#
# InstallerLogic
#
##########################################################################
class InstallerLogic():
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def installSoftware(self, sSourceDir, sInstallDir, qStBar):
        ''' Backup previous install if folder exists and it is not empty.
            Backup by renaming existing folder with .BAK-Date-Time suffix.
            
            Copy all files and folders into selected install dir.
        '''


        try:

            self.sSourceDir = sSourceDir
            self.sInstallDir = sInstallDir
            self.statusBar = qStBar
            qMsgBox = QtWidgets.QMessageBox()

            sPathInstall = Path(self.sInstallDir)
            bBackupComplete = False

            if sPathInstall.is_dir():
                # folder exists
                if len(os.listdir(sPathInstall)) > 0:
                    # folder not empty
                    qMsgBox.setIcon(QtWidgets.QMessageBox.Question)
                    qMsgBox.setText("Selected install folder exists.\nA backup will capture existing settings and results in the Inputs and Outputs folders.")
                    qMsgBox.setInformativeText( "Do you want to backup existing module?")
                    qMsgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    qMsgBox.setDefaultButton(QtWidgets.QMessageBox.Yes)
                    qAns = qMsgBox.exec()

                    if qAns == QtWidgets.QMessageBox.Yes:
                        
                        sCurrent_datetime = datetime.today().strftime('%Y%m%d-%H%M%S')
                        sPathBackupFolder = os.path.join (os.path.dirname(sPathInstall),\
                                                        os.path.basename(sPathInstall) + ".BAK-" + sCurrent_datetime)
                        qMsgBox.setIcon(QtWidgets.QMessageBox.Question)
                        qMsgBox.setText("Creating backup folder : ")
                        qMsgBox.setInformativeText( sPathBackupFolder )
                        qMsgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                        qAns = qMsgBox.exec()

                        if qAns == QtWidgets.QMessageBox.Ok:
                            os.rename(sPathInstall, sPathBackupFolder)
                            bBackupComplete = True
                            
                        
            # copy folders and subfolders to install dir
            qMsgBox.setIcon(QtWidgets.QMessageBox.Question)
            if bBackupComplete:
                sMsg = "Backup complete - installing code ..."
            else:
                sMsg = "Installing code ..."
            qMsgBox.setText(sMsg)
            sMsg = "Copying from : " + sSourceDir + " \nTo : " + str(sPathInstall)
            qMsgBox.setInformativeText( sMsg )
            qMsgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            qAns = qMsgBox.exec()

            if qAns == QtWidgets.QMessageBox.Ok:
                self.statusBar.showMessage("Copying .....")
                if os.path.exists(sPathInstall):
                    shutil.rmtree(sPathInstall)
                shutil.copytree(sSourceDir, sPathInstall)

                self.statusBar.showMessage("Done")

        except:
            tb = traceback.format_exc()
            self.statusBar.showMessage("!!! ERROR !!! ")
            qMsgBox = QtWidgets.QMessageBox()
            qMsgBox.setText("Error installing software to target directory")
            qMsgBox.setInformativeText(tb)
            qMsgBox.exec()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

    IQInstaller = ImageQuizzerInstallerWindow()
    IQInstaller.show()

    app.exec()
