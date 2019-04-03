import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
import PyQt5.QtWidgets as qw

import sys

MESSAGE_ERROR = 0
MESSAGE_INFORMATION = 1

styleSheet = None

with open("_ui_standalone/themes/default-theme.qss", "r") as styleFile:
    styleSheet = styleFile.read()

class QMessageDialog(qw.QDialog):
    def __init__(self, type, text, title = None):
        qw.QDialog.__init__(self)
        self.setWindowIcon(qg.QIcon("Circlelizer/icons/icon.png"))
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
            self.icon = qg.QPixmap("Circlelizer/icons/about.png")
        elif type == MESSAGE_INFORMATION:
            self.setWindowTitle("Information")
            self.icon = qg.QPixmap("Circlelizer/icons/about.png")

    def initUI(self):
        layout = qw.QGridLayout()

        # Image 0 0
        self.l_image = qw.QLabel()
        self.l_image.setPixmap(self.icon)
        layout.addWidget(self.l_image, 0, 0)
        
        # Info text
        self.l_info = qw.QLabel(self.text)
        self.l_info.setWordWrap(True)
        self.l_info.setMaximumWidth(400)
        layout.addWidget(self.l_info, 0, 1)

        # Buttons
        self.ok_button = qw.QDialogButtonBox(qw.QDialogButtonBox.Ok)
        self.ok_button.accepted.connect(self.On_OkPressed)
        layout.addWidget(self.ok_button, 1,1)

        self.setLayout(layout)

    def On_OkPressed(self):
        self.close()



if __name__ == "__main__":
    app = qw.QApplication(sys.argv)
    qerror = QMessageDialog(MESSAGE_INFORMATION, "You need to specify a correct number in order to rotate the object!", "About")
    qerror.exec()
    sys.exit(app.exec_())