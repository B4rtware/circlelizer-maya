import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
import PyQt5.QtWidgets as qw

import sys
import os

styleSheet = None

with open("_ui_standalone/themes/default-theme.qss", "r") as styleFile:
    styleSheet = styleFile.read()

aboutHTML = None
with open("_ui_standalone/html/about.html") as aboutFile:
    aboutHTML = aboutFile.read()

helpHTML = None
with open("_ui_standalone/html/help.html") as helpFile:
    helpHTML = helpFile.read()

class CirclelizerInfo(qw.QDialog):
    TEXT_AREA_HEIGHT = 400
    TEXT_AREA_WIDTH = 400

    def __init__(self):
        qw.QDialog.__init__(self)
        
        self.setWindowIcon(qg.QIcon("Circlelizer/icons/help.png"))
        self.setWindowTitle("Circlelizer Help")
        self.setStyleSheet(styleSheet)
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.initMainWidget()

    def initMainWidget(self):
        self.mainLayout = qw.QVBoxLayout()
        self.tabWidget = qw.QTabWidget()
        self.tabWidget.addTab(self.initTabHelp(),
                            qg.QIcon("Circlelizer/icons/help.png"),
                            "Help")
        self.tabWidget.addTab(self.initTabAbout(),
                            qg.QIcon("Circlelizer/icons/about.png"),
                            "About")
        
        self.mainLayout.addWidget(self.tabWidget)

        self.setLayout(self.mainLayout)

    def initTabHelp(self):
        self.tabHelp = qw.QWidget()
        self.tabHelp.setObjectName("tab-help")

        layout = qw.QVBoxLayout()

        self.te_help = qw.QTextBrowser()
        self.te_help.setReadOnly(True)
        self.te_help.setHtml(helpHTML)
        self.te_help.setFixedSize(self.TEXT_AREA_HEIGHT, self.TEXT_AREA_WIDTH)
        layout.addWidget(self.te_help)

        self.tabHelp.setLayout(layout)

        return self.tabHelp

    def initTabAbout(self):
        self.tabAbout = qw.QWidget()
        self.tabAbout.setObjectName("tab-about")

        layout = qw.QHBoxLayout()

        self.te_about = qw.QTextBrowser()
        self.te_about.setReadOnly(True)
        self.te_about.setHtml(aboutHTML)
        self.te_about.setMaximumSize(self.TEXT_AREA_HEIGHT,
                                     self.TEXT_AREA_WIDTH)
        layout.addWidget(self.te_about)

        self.tabAbout.setLayout(layout)

        return self.tabAbout

class Circlelizer(qw.QWidget):
    # Widgets Variables
    WIDGET_HEIGHT = 20
    SI_WIDTH = 50
    SI_NORMAL_XYZ_WIDTH = 25
    SI_MIDPOINT_XYZ_WIDTH = 50

    B_NORMAL_WIDTH = 25

    def __init__(self):
        qw.QWidget.__init__(self)
        self.infoDialog = CirclelizerInfo()

        self.setWindowIcon(qg.QIcon("Circlelizer/icons/icon.png"))
        self.setWindowTitle("Circlelizer")
        self.setObjectName("body")
        self.setWindowFlags(qc.Qt.FramelessWindowHint)
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setStyleSheet(styleSheet)
        self.initMainWidget()

    def initMainWidget(self):
        layout = qw.QGridLayout()

        # Header Label
        self.l_header = qw.QLabel()
        self.l_header.setPixmap(qg.QPixmap("Circlelizer/icons/header_70.png"))
        self.l_header.setAlignment(qc.Qt.AlignCenter)
        layout.addWidget(self.l_header, 0, 0)

        # Help Button
        icoHelp = qg.QIcon("Circlelizer/icons/help.png")
        self.b_help = qw.QPushButton()
        self.b_help.setObjectName("b_help")
        self.b_help.setIcon(icoHelp)
        self.b_help.setFixedSize(self.WIDGET_HEIGHT, self.WIDGET_HEIGHT)
        self.b_help.setIconSize(qc.QSize(self.WIDGET_HEIGHT,
                                         self.WIDGET_HEIGHT))
        self.b_help.setLayoutDirection(qc.Qt.RightToLeft)
        self.b_help.clicked.connect(self.On_HelpButton_Pressed)
        layout.addWidget(self.b_help, 0, 0, qc.Qt.AlignTop)

        # Tab Widgets
        self.t_basic = qw.QTabWidget()
        self.initTabBasic()
        layout.addWidget(self.t_basic, 1, 0)

        self.t_advanced = qw.QTabWidget()
        self.initTabAdvanced()
        layout.addWidget(self.t_advanced, 2, 0)

        # Circlelize Button
        self.b_circlize = qw.QPushButton("Circlelize")
        self.b_circlize.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.b_circlize, 3, 0)

        self.setLayout(layout)

    def initTabBasic(self):
        self.tabBasic = qw.QWidget()
        self.tabBasic.setObjectName("tab-basic")
        self.t_basic.addTab(self.tabBasic,
                            qg.QIcon("Circlelizer/icons/tool.png"),
                            "Basic")
        # Widgets
        layout = qw.QGridLayout()
        # 0 0 Radius Checkbox
        self.cb_radius = qw.QCheckBox("Smart Radius")
        self.cb_radius.setFixedHeight(self.WIDGET_HEIGHT)
        self.cb_radius.setChecked(True)
        self.cb_radius.stateChanged.connect(
            lambda value:
            self.On_SmartCheckBox_StateChanged(value,[self.si_radius,
                                                      self.l_radius]))
        layout.addWidget(self.cb_radius, 0, 0)

        # 1 0 MidPoint CheckBox
        self.cb_midPoint = qw.QCheckBox("Smart MidPoint")
        self.cb_midPoint.setFixedHeight(self.WIDGET_HEIGHT)
        self.cb_midPoint.setChecked(True)
        self.cb_midPoint.stateChanged.connect(
            lambda value:
            self.On_SmartCheckBox_StateChanged(value, [self.si_midPointX,
                                                       self.si_midPointY,
                                                       self.si_midPointZ,
                                                       self.l_midPoint]))
        layout.addWidget(self.cb_midPoint, 1, 0)

        # 0 1 Normal Checkbox
        self.cb_normal = qw.QCheckBox("Smart Normal")
        self.cb_normal.setFixedHeight(self.WIDGET_HEIGHT)
        self.cb_normal.setChecked(True)
        self.cb_normal.stateChanged.connect(
            lambda value:
            self.On_SmartCheckBox_StateChanged(value, [self.si_normalX,
                                                       self.si_normalY,
                                                       self.si_normalZ,
                                                       self.b_normalX,
                                                       self.b_normalY,
                                                       self.b_normalZ,
                                                       self.l_normal]))
        layout.addWidget(self.cb_normal, 0, 1)

        # 1 1 Project on Mesh
        self.cb_projectOnMesh = qw.QCheckBox("project on mesh")
        self.cb_projectOnMesh.setFixedHeight(self.WIDGET_HEIGHT)
        self.cb_projectOnMesh.setChecked(True)
        layout.addWidget(self.cb_projectOnMesh, 1, 1)

        self.tabBasic.setLayout(layout)

    def initTabAdvanced(self):
        self.tabAdvanced = qw.QWidget()
        self.tabAdvanced.setObjectName("tab-advanced")
        self.t_advanced.addTab(self.tabAdvanced,
                               qg.QIcon("Circlelizer/icons/advanced.png"),
                               "Advanced")

        # Widgets
        layout = qw.QGridLayout()

        # +--------+
        # | Radius |
        # +--------+

        # 0 1 Radius Label
        self.l_radius = qw.QLabel("Radius: ")
        self.l_radius.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.l_radius, 0, 0)

        # 0 2 Radius SlideInput
        self.si_radius = qw.QLineEdit()
        self.si_radius.setFixedSize(self.SI_WIDTH, self.WIDGET_HEIGHT)
        layout.addWidget(self.si_radius, 0, 1)

        # +--------+
        # | Degree |
        # +--------+

        self.l_degree = qw.QLabel("Degree:")
        self.l_degree.setFixedHeight(self.WIDGET_HEIGHT)
        self.l_degree.setFixedWidth(45)
        layout.addWidget(self.l_degree, 0, 2)

        self.si_degree = qw.QLineEdit()
        self.si_degree.setText("360.0")
        self.si_degree.setFixedSize(self.SI_WIDTH, self.WIDGET_HEIGHT)
        self.si_degree.setToolTip("does not 100% works with my calculations you"\
                                  "\nhave to manual adjust "\
                                  "the rotation and scale.")
        layout.addWidget(self.si_degree, 0, 3)

        # +----------+
        # | MidPoint |
        # +----------+

        # 2 1 MidPoint Label
        self.l_midPoint = qw.QLabel("MidPoint: ")
        self.l_midPoint.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.l_midPoint, 1, 0)

        # 2 2 MidPoint SlideInput X
        self.si_midPointX = qw.QLineEdit()
        self.si_midPointX.setFixedWidth(self.SI_MIDPOINT_XYZ_WIDTH)
        self.si_midPointX.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.si_midPointX, 1, 1)

        # 2 3 MidPoint SlideInput Y
        self.si_midPointY = qw.QLineEdit()
        self.si_midPointY.setFixedWidth(self.SI_MIDPOINT_XYZ_WIDTH)
        self.si_midPointY.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.si_midPointY, 1, 2)

        # 2 4 MidPoint SlideInput Z
        self.si_midPointZ = qw.QLineEdit()
        self.si_midPointZ.setFixedWidth(self.SI_MIDPOINT_XYZ_WIDTH)
        self.si_midPointZ.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.si_midPointZ, 1, 3)

        # +--------+
        # | Normal |
        # +--------+

        # 2 0 Normal Label
        self.l_normal = qw.QLabel("Circle Normal:")
        self.l_normal.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.l_normal, 2, 0)

        # 2 1 Child Normal X HBoxLayout
        # -----------------------------
        childNormalXLayout = qw.QHBoxLayout()

        # 0 0 Normal SlideInput X
        self.si_normalX = qw.QLineEdit()
        self.si_normalX.setFixedWidth(self.SI_NORMAL_XYZ_WIDTH)
        self.si_normalX.setFixedHeight(self.WIDGET_HEIGHT)
        childNormalXLayout.addWidget(self.si_normalX)

        # 0 1 Normal Button X 
        self.b_normalX = qw.QPushButton("X")
        self.b_normalX.setFixedWidth(self.B_NORMAL_WIDTH)
        self.b_normalX.setFixedHeight(self.WIDGET_HEIGHT)
        self.b_normalX.setObjectName("xyz")
        self.b_normalX.pressed.connect(lambda:self.On_AxisButton_Pressed("X"))
        childNormalXLayout.addWidget(self.b_normalX)

        layout.addItem(childNormalXLayout, 2, 1)

        # 2 2 Child Normal Y HBoxLayout
        # -----------------------------
        childNormalYLayout = qw.QHBoxLayout()

        # 0 0 Normal SlideInput Y
        self.si_normalY = qw.QLineEdit()
        self.si_normalY.setFixedWidth(self.SI_NORMAL_XYZ_WIDTH)
        self.si_normalY.setFixedHeight(self.WIDGET_HEIGHT)
        childNormalYLayout.addWidget(self.si_normalY)

        # 0 1 Normal Button Y
        self.b_normalY = qw.QPushButton("Y")
        self.b_normalY.setFixedWidth(self.B_NORMAL_WIDTH)
        self.b_normalY.setFixedHeight(self.WIDGET_HEIGHT)
        self.b_normalY.setObjectName("xyz")
        self.b_normalY.pressed.connect(lambda:self.On_AxisButton_Pressed("Y"))
        childNormalYLayout.addWidget(self.b_normalY)

        layout.addItem(childNormalYLayout, 2, 2)

        # 2 3 Child Normal Z HBoxLayout
        # -----------------------------
        childNormalZLayout = qw.QHBoxLayout()

        # 0 0 Normal SlideInput Z
        self.si_normalZ = qw.QLineEdit()
        self.si_normalZ.setFixedWidth(self.SI_NORMAL_XYZ_WIDTH)
        self.si_normalZ.setFixedHeight(self.WIDGET_HEIGHT)
        childNormalZLayout.addWidget(self.si_normalZ)

        # 0 1 Normal Button Z
        self.b_normalZ = qw.QPushButton("Z")
        self.b_normalZ.setFixedWidth(self.B_NORMAL_WIDTH)
        self.b_normalZ.setFixedHeight(self.WIDGET_HEIGHT)
        self.b_normalZ.pressed.connect(lambda:self.On_AxisButton_Pressed("Z"))
        childNormalZLayout.addWidget(self.b_normalZ)

        layout.addItem(childNormalZLayout, 2, 3)

        # Call events
        self.cb_radius.stateChanged.emit(2)
        self.cb_midPoint.stateChanged.emit(2)
        self.cb_normal.stateChanged.emit(2)

        self.tabAdvanced.setLayout(layout)

    def initTabWidgets_old(self):
        self.tabHelp = qw.QWidget()
        self.tabBasic.setObjectName("tab-help")
        self.tabAbout = qw.QWidget()
        self.tabBasic.setObjectName("tab-about")

        self.t_widget.addTab(self.tabBasic,
                             qg.QIcon("Circlelizer/icons/tool.png"),
                             "Basic")
        self.t_widget.addTab(self.tabAdvanced,
                             qg.QIcon("Circlelizer/icons/advanced.png"),
                             "Advanced")
        self.t_widget.addTab(self.tabHelp,
                             qg.QIcon("Circlelizer/icons/help.png"),
                             "Help")
        self.t_widget.addTab(self.tabAbout,
                             qg.QIcon("Circlelizer/icons/about.png"),
                            "About")

        self.initTabTool()
        self.initTabAdvanced()
        self.initTabHelp()
        self.initTabAbout()

    def initTabTool_old(self):
        layout = qw.QGridLayout()

        #+----------+
        #| 0 Radius |
        #+----------+

        # 0 0 Radius Checkbox
        self.cb_radius = qw.QCheckBox("Smart Radius")
        self.cb_radius.setFixedHeight(self.WIDGET_HEIGHT)
        self.cb_radius.setChecked(True)
        self.cb_radius.stateChanged.connect(
            lambda value:
            self.On_SmartCheckBox_StateChanged(value,[self.si_radius,
                                                      self.l_radius]))
        layout.addWidget(self.cb_radius, 0, 0)

        # 0 1 Radius Label
        self.l_radius = qw.QLabel("Radius: ")
        self.l_radius.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.l_radius, 0, 1)

        # 0 2 Radius SlideInput
        self.si_radius = qw.QLineEdit()
        self.si_radius.setFixedSize(self.SI_WIDTH, self.WIDGET_HEIGHT)
        layout.addWidget(self.si_radius, 0, 2, 1, 2)

        #+------------+
        #| 1 MidPoint |
        #+------------+

        # 1 0 MidPoint CheckBox
        self.cb_midPoint = qw.QCheckBox("Smart MidPoint")
        self.cb_midPoint.setFixedHeight(self.WIDGET_HEIGHT)
        self.cb_midPoint.setChecked(True)
        self.cb_midPoint.stateChanged.connect(
            lambda value:
            self.On_SmartCheckBox_StateChanged(value, [self.si_midPointX,
                                                       self.si_midPointY,
                                                       self.si_midPointZ,
                                                       self.l_midPoint]))
        layout.addWidget(self.cb_midPoint, 1, 0)

        # 2 1 MidPoint Label
        self.l_midPoint = qw.QLabel("MidPoint: ")
        self.l_midPoint.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.l_midPoint, 1, 1)

        # 2 2 MidPoint SlideInput X
        self.si_midPointX = qw.QLineEdit()
        self.si_midPointX.setFixedWidth(self.SI_MIDPOINT_XYZ_WIDTH)
        self.si_midPointX.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.si_midPointX, 1, 2)

        # 2 3 MidPoint SlideInput Y
        self.si_midPointY = qw.QLineEdit()
        self.si_midPointY.setFixedWidth(self.SI_MIDPOINT_XYZ_WIDTH)
        self.si_midPointY.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.si_midPointY, 1, 3)

        # 2 4 MidPoint SlideInput Z
        self.si_midPointZ = qw.QLineEdit()
        self.si_midPointZ.setFixedWidth(self.SI_MIDPOINT_XYZ_WIDTH)
        self.si_midPointZ.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.si_midPointZ, 1, 4)

        #+----------+
        #| 2 Normal |
        #+----------+
        
        # 2 0 Normal Checkbox
        self.cb_normal = qw.QCheckBox("Smart Normal")
        self.cb_normal.setFixedHeight(self.WIDGET_HEIGHT)
        self.cb_normal.setChecked(True)
        self.cb_normal.stateChanged.connect(
            lambda value:
            self.On_SmartCheckBox_StateChanged(value, [self.si_normalX,
                                                       self.si_normalY,
                                                       self.si_normalZ,
                                                       self.b_normalX,
                                                       self.b_normalY,
                                                       self.b_normalZ,
                                                       self.l_normal]))
        layout.addWidget(self.cb_normal, 2, 0)

        # 2 1 Normal Label
        self.l_normal = qw.QLabel("Circle Normal:")
        self.l_normal.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.l_normal, 2, 1)

        # 2 2 Child Normal X HBoxLayout
        # -----------------------------
        childNormalXLayout = qw.QHBoxLayout()

        # 0 0 Normal SlideInput X
        self.si_normalX = qw.QLineEdit()
        self.si_normalX.setFixedWidth(self.SI_NORMAL_XYZ_WIDTH)
        self.si_normalX.setFixedHeight(self.WIDGET_HEIGHT)
        childNormalXLayout.addWidget(self.si_normalX)

        # 0 1 Normal Button X 
        self.b_normalX = qw.QPushButton("X")
        self.b_normalX.setFixedWidth(self.B_NORMAL_WIDTH)
        self.b_normalX.setFixedHeight(self.WIDGET_HEIGHT)
        self.b_normalX.setObjectName("xyz")
        self.b_normalX.pressed.connect(lambda:self.On_AxisButton_Pressed("X"))
        childNormalXLayout.addWidget(self.b_normalX)

        layout.addItem(childNormalXLayout)

        # 2 3 Child Normal Y HBoxLayout
        # -----------------------------
        childNormalYLayout = qw.QHBoxLayout()

        # 0 0 Normal SlideInput Y
        self.si_normalY = qw.QLineEdit()
        self.si_normalY.setFixedWidth(self.SI_NORMAL_XYZ_WIDTH)
        self.si_normalY.setFixedHeight(self.WIDGET_HEIGHT)
        childNormalYLayout.addWidget(self.si_normalY)

        # 0 1 Normal Button Y
        self.b_normalY = qw.QPushButton("Y")
        self.b_normalY.setFixedWidth(self.B_NORMAL_WIDTH)
        self.b_normalY.setFixedHeight(self.WIDGET_HEIGHT)
        self.b_normalY.setObjectName("xyz")
        self.b_normalY.pressed.connect(lambda:self.On_AxisButton_Pressed("Y"))
        childNormalYLayout.addWidget(self.b_normalY)

        layout.addItem(childNormalYLayout, 2, 3)

        # 2 4 Child Normal Z HBoxLayout
        # -----------------------------
        childNormalZLayout = qw.QHBoxLayout()

        # 0 0 Normal SlideInput Z
        self.si_normalZ = qw.QLineEdit()
        self.si_normalZ.setFixedWidth(self.SI_NORMAL_XYZ_WIDTH)
        self.si_normalZ.setFixedHeight(self.WIDGET_HEIGHT)
        childNormalZLayout.addWidget(self.si_normalZ)

        # 0 1 Normal Button Z
        self.b_normalZ = qw.QPushButton("Z")
        self.b_normalZ.setFixedWidth(self.B_NORMAL_WIDTH)
        self.b_normalZ.setFixedHeight(self.WIDGET_HEIGHT)
        self.b_normalZ.pressed.connect(lambda:self.On_AxisButton_Pressed("Z"))
        childNormalZLayout.addWidget(self.b_normalZ)

        layout.addItem(childNormalZLayout, 2, 4)

        # Call events
        self.cb_radius.stateChanged.emit(2)
        self.cb_midPoint.stateChanged.emit(2)
        self.cb_normal.stateChanged.emit(2)

        self.tabBasic.setLayout(layout)

    def initTabAdvanced_old(self):
        layout = qw.QGridLayout()
        #layout.expandingDirections()
        layout.setAlignment(qc.Qt.AlignLeft)
        # 0 0 Child Degree HBoxLayout
        # -----------------------
        childDegreeLayout = qw.QHBoxLayout()

        self.l_degree = qw.QLabel("Degree:")
        self.l_degree.setFixedHeight(self.WIDGET_HEIGHT)
        self.l_degree.setFixedWidth(45)
        childDegreeLayout.addWidget(self.l_degree)

        self.si_degree = qw.QLineEdit()
        self.si_degree.setText("360.0")
        self.si_degree.setFixedSize(self.SI_WIDTH, self.WIDGET_HEIGHT)
        self.si_degree.setToolTip("does not 100% works with my calculations you"\
                                  "\nhave to manual adjust "\
                                  "the rotation and scale.")
        childDegreeLayout.addWidget(self.si_degree)

        layout.addItem(childDegreeLayout, 0, 0)
        
        # 0 1 Extract Border Checkbox
        self.cb_extractBorder = qw.QCheckBox("extract border")
        self.cb_extractBorder.setFixedHeight(self.WIDGET_HEIGHT)
        self.cb_extractBorder.setChecked(True)
        self.cb_extractBorder.setToolTip("my current algorithm does only "\
                                         "\nspecify border edges if"\
                                         "\nthey have neighbours which are"\
                                         "\nnot in the selected list"\
                                         "\nbut it can occur that a vertex"\
                                         "\nis not in the list and is still"\
                                         "\na border vertex.")
        layout.addWidget(self.cb_extractBorder, 1, 0)

        # 0 2 Project on Mesh
        self.cb_projectOnMesh = qw.QCheckBox("project on mesh")
        self.cb_projectOnMesh.setFixedHeight(self.WIDGET_HEIGHT)
        self.cb_projectOnMesh.setChecked(True)
        layout.addWidget(self.cb_projectOnMesh, 2, 0)

        self.tabAdvanced.setLayout(layout)

    def initTabHelp_old(self):
        layout = qw.QGridLayout()

        self.te_help = qw.QTextBrowser()
        self.te_help.setReadOnly(True)
        self.te_help.setHtml(helpHTML)
        self.te_help.setFixedHeight(self.TEXT_AREA_HEIGHT)
        layout.addWidget(self.te_help)

        self.tabHelp.setLayout(layout)
    
    def initTabAbout_old(self):
        layout = qw.QGridLayout()

        self.te_about = qw.QTextBrowser()
        self.te_about.setReadOnly(True)
        self.te_about.setHtml(aboutHTML)
        self.te_about.setMaximumHeight(self.TEXT_AREA_HEIGHT)
        layout.addWidget(self.te_about)

        self.tabAbout.setLayout(layout)

    def On_SmartCheckBox_StateChanged(self, value, instances):
        if value == 2:
            for instance in instances:
                instance.setDisabled(1)
        elif value == 0:
            for instance in instances:
                instance.setDisabled(0)

    def On_HelpButton_Pressed(self, value):
        self.infoDialog.show()

    def On_AxisButton_Pressed(self, axis):
        if axis == "X":
            self.si_normalX.setText("1.0")
            self.si_normalY.setText("0.0")
            self.si_normalZ.setText("0.0")
        elif axis == "Y":
            self.si_normalX.setText("0.0")
            self.si_normalY.setText("1.0")
            self.si_normalZ.setText("0.0")
        elif axis == "Z":
            self.si_normalX.setText("0.0")
            self.si_normalY.setText("0.0")
            self.si_normalZ.setText("1.0")

    def On_CirclizeButton_Pressed(self):
        partialCirclelize = partial(cmds.circlelize)

        if not self.cb_radius.isChecked():
            radius = float(self.si_radius.text())
            partialCirclelize.keywords["r"] = radius

        if not self.cb_midPoint.isChecked():
            midPoint = (float(self.si_midPointX),
                        float(self.si_midPointY),
                        float(self.si_midPointZ))
            partialCirclelize.keywords["m"] = midPoint

        if not self.cb_normal.isChecked():
            normal = (float(self.si_normalX),
                      float(self.si_normalY),
                      float(self.si_normalZ))
            partialCirclelize.keywords["cn"] = normal

        partialCirclelize()

class Window(qw.QWidget):
    def __init__(self):
        qw.QWidget.__init__(self)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Circlelizer")

        # constants
        SI_WIDTH = 50
        WIDGET_HEIGHT = 20
        SI_VALIDATOR = qg.QDoubleValidator(-99, 99,3)
        SI_NORMAL_XYZ_WIDTH = 25
        SI_MIDPOINT_XYZ_WIDTH = 50

        B_NORMAL_WIDTH = 20


        gridLayout = qw.QGridLayout()

        #+---------+
        #| 0 Title |
        #+---------+
        self.l_title = qw.QLabel("Circlelizer")
        self.l_title.setAlignment(qc.Qt.AlignHCenter)
        gridLayout.addWidget(self.l_title, 0, 0, 1, 5)

        #+----------+
        #| 1 Radius |
        #+----------+

        # 1 0 Radius Checkbox
        self.cb_radius = qw.QCheckBox("Smart Radius")
        self.cb_radius.setFixedHeight(WIDGET_HEIGHT)
        self.cb_radius.setChecked(True)
        self.cb_radius.stateChanged.connect(
            lambda value:
            self.On_SmartCheckBox_StateChanged(value,[self.si_radius,
                                                      self.l_radius]))
        gridLayout.addWidget(self.cb_radius, 1, 0)

        # 1 1 Radius Label
        self.l_radius = qw.QLabel("Radius: ")
        self.l_radius.sdetFixedHeight(WIDGET_HEIGHT)
        gridLayout.addWidget(self.l_radius, 1, 1)

        # 1 2 Radius SlideInput
        self.si_radius = qw.QLineEdit()
        self.si_radius.setValidator(qg.QDoubleValidator(-99, 99,3))
        self.si_radius.setFixedWidth(SI_WIDTH)
        self.l_radius.setFixedHeight(WIDGET_HEIGHT)
        gridLayout.addWidget(self.si_radius, 1, 2, 1, 2)

        #+------------+
        #| 2 MidPoint |
        #+------------+

        # 2 0 MidPoint CheckBox
        self.cb_midPoint = qw.QCheckBox("Smart MidPoint")
        self.cb_midPoint.setFixedHeight(WIDGET_HEIGHT)
        self.cb_midPoint.setChecked(True)
        self.cb_midPoint.stateChanged.connect(
            lambda value:
            self.On_SmartCheckBox_StateChanged(value, [self.si_midPointX,
                                                       self.si_midPointY,
                                                       self.si_midPointZ,
                                                       self.l_midPoint]))
        gridLayout.addWidget(self.cb_midPoint, 2, 0)

        # 2 1 MidPoint Label
        self.l_midPoint = qw.QLabel("MidPoint: ")
        self.l_midPoint.setFixedHeight(WIDGET_HEIGHT)
        gridLayout.addWidget(self.l_midPoint, 2, 1)

        # 2 2 MidPoint SlideInput X
        self.si_midPointX = qw.QLineEdit()
        self.si_midPointX.setFixedWidth(SI_MIDPOINT_XYZ_WIDTH)
        self.si_midPointX.setFixedHeight(WIDGET_HEIGHT)
        gridLayout.addWidget(self.si_midPointX, 2, 2)

        # 2 3 MidPoint SlideInput Y
        self.si_midPointY = qw.QLineEdit()
        self.si_midPointY.setFixedWidth(SI_MIDPOINT_XYZ_WIDTH)
        self.si_midPointY.setFixedHeight(WIDGET_HEIGHT)
        gridLayout.addWidget(self.si_midPointY, 2, 3)

        # 2 4 MidPoint SlideInput Z
        self.si_midPointZ = qw.QLineEdit()
        self.si_midPointZ.setFixedWidth(SI_MIDPOINT_XYZ_WIDTH)
        self.si_midPointZ.setFixedHeight(WIDGET_HEIGHT)
        gridLayout.addWidget(self.si_midPointZ, 2, 4)

        #+----------+
        #| 3 Normal |
        #+----------+
        
        # 3 0 Normal Checkbox
        self.cb_normal = qw.QCheckBox("Smart Normal")
        self.cb_normal.setFixedHeight(WIDGET_HEIGHT)
        self.cb_normal.setChecked(True)
        self.cb_normal.stateChanged.connect(
            lambda value:
            self.On_SmartCheckBox_StateChanged(value, [self.si_normalX,
                                                       self.si_normalY,
                                                       self.si_normalZ,
                                                       self.b_normalX,
                                                       self.b_normalY,
                                                       self.b_normalZ,
                                                       self.l_normal]))
        gridLayout.addWidget(self.cb_normal, 3, 0)

        # 3 1 Normal Label
        self.l_normal = qw.QLabel("Circle Normal:")
        self.l_normal.setFixedHeight(WIDGET_HEIGHT)
        gridLayout.addWidget(self.l_normal, 3, 1)

        # 3 2 Child Normal X GridLayout
        # -----------------------------
        childNormalXGridLayout = qw.QGridLayout()
        childNormalXGridLayout.setHorizontalSpacing(0)

        # 0 0 Normal SlideInput X
        self.si_normalX = qw.QLineEdit()
        self.si_normalX.setFixedWidth(SI_NORMAL_XYZ_WIDTH)
        self.si_normalX.setFixedHeight(WIDGET_HEIGHT)
        childNormalXGridLayout.addWidget(self.si_normalX, 0, 0)

        # 0 1 Normal Button X 
        self.b_normalX = qw.QPushButton("X")
        self.b_normalX.setFixedWidth(B_NORMAL_WIDTH)
        self.b_normalX.setFixedHeight(WIDGET_HEIGHT)
        self.b_normalX.pressed.connect(lambda:self.On_AxisButton_Pressed("X"))
        childNormalXGridLayout.addWidget(self.b_normalX, 0, 1)

        gridLayout.addItem(childNormalXGridLayout, 3, 2)

        # 3 3 Child Normal Y GridLayout
        # -----------------------------
        childNormalYGridLayout = qw.QGridLayout()
        childNormalYGridLayout.setHorizontalSpacing(0)

        # 0 0 Normal SlideInput Y
        self.si_normalY = qw.QLineEdit()
        self.si_normalY.setFixedWidth(SI_NORMAL_XYZ_WIDTH)
        self.si_normalY.setFixedHeight(WIDGET_HEIGHT)
        childNormalYGridLayout.addWidget(self.si_normalY, 0, 0)

        # 0 1 Normal Button Y
        self.b_normalY = qw.QPushButton("Y")
        self.b_normalY.setFixedWidth(B_NORMAL_WIDTH)
        self.b_normalY.setFixedHeight(WIDGET_HEIGHT)
        self.b_normalY.pressed.connect(lambda:self.On_AxisButton_Pressed("Y"))
        childNormalYGridLayout.addWidget(self.b_normalY, 0, 1)

        gridLayout.addItem(childNormalYGridLayout, 3, 3)

        # 3 4 Child Normal Z GridLayout
        # -----------------------------
        childNormalZGridLayout = qw.QGridLayout()
        childNormalZGridLayout.setHorizontalSpacing(0)

        # 0 0 Normal SlideInput Z
        self.si_normalZ = qw.QLineEdit()
        self.si_normalZ.setFixedWidth(SI_NORMAL_XYZ_WIDTH)
        self.si_normalZ.setFixedHeight(WIDGET_HEIGHT)
        childNormalZGridLayout.addWidget(self.si_normalZ, 0, 0)

        # 0 1 Normal Button Z
        self.b_normalZ = qw.QPushButton("Z")
        self.b_normalZ.setFixedWidth(B_NORMAL_WIDTH)
        self.b_normalZ.setFixedHeight(WIDGET_HEIGHT)
        self.b_normalZ.pressed.connect(lambda:self.On_AxisButton_Pressed("Z"))
        childNormalZGridLayout.addWidget(self.b_normalZ, 0, 1)

        gridLayout.addItem(childNormalZGridLayout)

        #+-------------+
        #| 4 Seperator |
        #+-------------+ 

        # 4 0 Seprator Frame
        self.seperator = qw.QFrame()
        self.seperator.setFrameShape(qw.QFrame.HLine)
        gridLayout.addWidget(self.seperator, 4, 0, 1, 5)

        #+--------------+
        #| 5 Circlelize |
        #+--------------+

        # 5 0 Circlelize Button
        self.b_circlize = qw.QPushButton("Circlelize")
        gridLayout.addWidget(self.b_circlize, 5, 0, 1, 5)

        #+
        #| 6 
        #+

        # Call events
        self.cb_radius.stateChanged.emit(2)
        self.cb_midPoint.stateChanged.emit(2)
        self.cb_normal.stateChanged.emit(2)

        self.setLayout(gridLayout)

    def On_SmartCheckBox_StateChanged(self, value, instances):
        if value == 2:
            for instance in instances:
                instance.setDisabled(1)
        elif value == 0:
            for instance in instances:
                instance.setDisabled(0)

    def On_AxisButton_Pressed(self, axis):
        if axis == "X":
            self.si_normalX.setText("1.0")
            self.si_normalY.setText("0.0")
            self.si_normalZ.setText("0.0")
        elif axis == "Y":
            self.si_normalX.setText("0.0")
            self.si_normalY.setText("1.0")
            self.si_normalZ.setText("0.0")
        elif axis == "Z":
            self.si_normalX.setText("0.0")
            self.si_normalY.setText("0.0")
            self.si_normalZ.setText("1.0")


if __name__ == '__main__':

    app = qw.QApplication(sys.argv)
    window = Circlelizer()
    window.show()
    sys.exit(app.exec_())