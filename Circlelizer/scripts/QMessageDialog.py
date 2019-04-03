#+----------------------------------------------+
#| Version Selection use 2017 or 2016 and below |
#+----------------------------------------------+
# try load load pyside2 which is used in 2017 and above
try:
    import PySide2.QtCore as qc 
    import PySide2.QtGui as qg
    import PySide2.QtWidgets as qw
except ImportError:
    import PySide.QtCore as qc
    import PySide.QtGui as qg
    # importing twice because under pyside2 a new submodule
    # was named QWidgets
    import PySide.QtGui as qw

import sys
import os
import maya.api.OpenMaya as om

# resolve the resource file paths
themes_path = os.environ["CIRCLELIZER_THEMES_PATH"]
resources_path_unresolved = os.environ["XBMLANGPATH"]

fileObject = om.MFileObject()
fileObject.resolveMethod = om.MFileObject.kExact
fileObject.setRawPath(resources_path_unresolved)
fileObject.setRawName("header.png")
resources_path = fileObject.resolvedPath()

# load the style files which are needed
styleSheet = None
with open(themes_path + "/default-theme.qss","r") as styleFile:
    styleSheet = styleFile.read()

MESSAGE_ERROR = 0
MESSAGE_INFORMATION = 1

class QMessageDialog(qw.QDialog):
    def __init__(self, type, text, title = None):
        qw.QDialog.__init__(self)
        self.setWindowIcon(qg.QIcon(resources_path + "icon.png"))
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setStyleSheet(styleSheet)
        self.text = text

        self.icon = None
        self.initType(type)

        if title != None:
            self.setWindowTitle(title)

        self.initUI()

    def initType(self, type):
        if type == MESSAGE_ERROR:
            self.setWindowTitle("Error")
            self.icon = qg.QPixmap(resources_path + "about.png")
        elif type == MESSAGE_INFORMATION:
            self.setWindowTitle("Information")
            self.icon = qg.QPixmap(resources_path + "about.png")

    def initUI(self):
        layout = qw.QGridLayout()

        # Image 0 0
        self.l_image = qw.QLabel()
        self.l_image.setPixmap(self.icon)
        layout.addWidget(self.l_image, 0, 0)
        
        # Info text
        self.l_info = qw.QLabel(self.text)
        self.l_info.setWordWrap(True)
        self.l_info.setMaximumWidth(450)
        layout.addWidget(self.l_info, 0, 1)

        # Buttons
        self.ok_button = qw.QDialogButtonBox(qw.QDialogButtonBox.Ok)
        self.ok_button.accepted.connect(self.On_OkPressed)
        layout.addWidget(self.ok_button, 1,1)

        self.setLayout(layout)

    def On_OkPressed(self):
        self.close()