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

#+---------------------------------------------------------------------------+
#|                           QSlideInput Widget                              |
#|                                                                           |
#| -> my implementation of maya's slide input widget for QT                  |
#+---------------------------------------------------------------------------+

class QSlideInput(qw.QLineEdit):
    """own implementation of the maya's slide input widget
    Date: 23.09.2016
    Author: LifeArtist"""

    # an public event you can bind to from outside
    # and which notifies if the value has changed or not
    valueChangedEvent = qc.Signal()

    def __init__(self, *args, **kwargs):
        qw.QLineEdit.__init__(self, *args, **kwargs)
        self.init()
        self.initUi()

    def init(self):
        self.dragFlipped = False
        # how many pixels you have to move the mouse to increse or decrease
        # the value
        self.incdecSteps = 4
        self._currentStep = 0
        self.lastCoordValueX = 0
        self.dragBeginCount = 9
        self._dragCurrentCount = 0
        # value which will be added or substracted
        self.incdecrementor = 1
        self.lastMousePressedPos = qc.QPoint()

    def initUi(self):
        self.canSetFocusOnInput = True
        self.setFocusPolicy(qc.Qt.NoFocus)
        self.returnPressed.connect(self.clearFocus)
        self.setCursor(qc.Qt.SplitHCursor)
        self.setMouseTracking(0)
        self.setText("0.0")
        self.setValidator(qg.QDoubleValidator())

    def mouseMoveEvent(self, event):
        if not self.hasFocus():
            # +---------------------+
            # | enables drag events |
            # +---------------------+
            if self._dragCurrentCount == self.dragBeginCount:
                self.on_dragEnter()

            if self._dragCurrentCount >= self.dragBeginCount:
                self.on_drag()

            self._dragCurrentCount += 1

    def mousePressEvent(self, event):
        self.setMouseTracking(1)
        self.lastMousePressedPos = qg.QCursor.pos()
        self.lastCoordValueX = qg.QCursor.pos().x()

    def keyPressEvent(self, event):
        return super(QSlideInput, self).keyPressEvent(event)

    def mouseReleaseEvent(self, event):
        """function will be called if the mouse was released"""
        self.setMouseTracking(0)
        self._dragCurrentCount = 0
        self.setCursor(qc.Qt.SplitHCursor)
        # if the mouse was released we need to put the mouse to its last pos
        qg.QCursor.setPos(self.lastMousePressedPos)

        if self.canSetFocusOnInput:
            self.setFocus()
        else:
            self.canSetFocusOnInput = True

    def on_dragEnter(self):
        """function will be called if the mouse was hold down for the amount
        of dragBeginCount"""

        self.canSetFocusOnInput = False
        self.setCursor(qc.Qt.BlankCursor)

    def on_drag(self):
        """function will be called everytime you drag your mouse but first
        after on_dragEnter"""

        currentX = qg.QCursor.pos().x()

        if self.incdecSteps == self._currentStep:
            # +----------------------------------------------+
            # | check whether strg, shift is pressed or none |
            # +----------------------------------------------+
            modifiers = qw.QApplication.queryKeyboardModifiers()

            if modifiers == qc.Qt.ControlModifier:
                self.incdecrementor = 0.1
            elif modifiers == qc.Qt.ShiftModifier:
                self.incdecrementor = 10 
            else:
                self.incdecrementor = 1

            # +---------------------------------+
            # | addition and substraction logic |
            # +---------------------------------+
            currentValue = float(self.text())
            # determinds if its incremented or decremented
            if self.lastCoordValueX < currentX:
                currentValue += self.incdecrementor 
            elif self.lastCoordValueX > currentX:
                currentValue -= self.incdecrementor
            # sets the new text
            self.setText(str(currentValue))
            # emit event
            self.valueChangedEvent.emit()

            self.lastCoordValueX = currentX
            self._currentStep = 0
        else:
            self._currentStep += 1

        # reset the cursor if it reaches the end of the screen
        desktopWidth = qw.QApplication.desktop().availableGeometry().width()

        if currentX == (desktopWidth - 1):
            qg.QCursor.setPos(0, qg.QCursor.pos().y())
        elif currentX == 0:
            qg.QCursor.setPos(desktopWidth - 1, qg.QCursor.pos().y())