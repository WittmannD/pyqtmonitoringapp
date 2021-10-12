from PyQt5.QtCore import QObject, QCoreApplication, pyqtSlot, QEvent, QPoint, Qt
from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtWidgets import QWidget


class Backend(QObject):
    def __init__(self, parent):
        super(Backend, self).__init__(parent)
        self.browser = parent

    def _sendMouseEvent(self, event, point):
        event = QMouseEvent(event, point, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        render_widget = self.browser.view().findChild(QWidget)
        QCoreApplication.postEvent(render_widget, event)

    def _sendKeyEvent(self, key, text):
        event = QKeyEvent(QEvent.KeyPress, key, Qt.NoModifier, text=text)
        render_widget = self.browser.view().findChild(QWidget)
        QCoreApplication.postEvent(render_widget, event)

        event = QKeyEvent(QEvent.KeyRelease, key, Qt.NoModifier, '')
        QCoreApplication.postEvent(render_widget, event)

    @pyqtSlot(list)
    def clickTo(self, position):
        point = QPoint(*position)

        self._sendMouseEvent(QEvent.MouseMove, point)
        self._sendMouseEvent(QEvent.MouseButtonPress, point)
        self._sendMouseEvent(QEvent.MouseButtonRelease, point)

        return

    @pyqtSlot(str)
    def typeText(self, text):
        for letter in text:
            self._sendKeyEvent(0, letter)

        return

    @pyqtSlot(str)
    def sendKey(self, key_code):
        self._sendKeyEvent(Qt.__dict__[key_code], '')

        return
