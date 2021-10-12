from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, pyqtProperty

from models.models import PreparedTitleDataModel, MonitorDataModel
from utils.Singleton import Singleton


class Controller(QObject, metaclass=Singleton):
    # signals for emitting from client app
    tabReady = pyqtSignal()
    createTabs = pyqtSignal(int)

    addMonitor = pyqtSignal(str)
    removeMonitor = pyqtSignal(str)
    changeAutoMode = pyqtSignal(bool)

    addTitleForSend = pyqtSignal(str)
    completeAndSend = pyqtSignal(str)
    titleSent = pyqtSignal(str)

    # signals for callback to client app
    commitTab = pyqtSignal(bool)
    commitTitle = pyqtSignal(str)
    commitMonitor = pyqtSignal(str)
    setTitleStatus = pyqtSignal(str)

    openCoverInExplorer = pyqtSignal(str)
    openLinkInBrowser = pyqtSignal(str)

    _initialData = None

    @pyqtSlot(int)
    def createTabsEmit(self, count):
        self.createTabs.emit(count)

    @pyqtSlot()
    def tabReadyEmit(self):
        self.tabReady.emit()

    @pyqtSlot(str)
    def addMonitorEmit(self, monitorData: str):
        self.addMonitor.emit(monitorData)

    @pyqtSlot(str)
    def removeMonitorEmit(self, uid: str):
        self.removeMonitor.emit(uid)

    @pyqtSlot(bool)
    def changeAutoModeEmit(self, state: bool):
        self.changeAutoMode.emit(state)

    @pyqtSlot(str)
    def addTitleForSendEmit(self, titleData: str):
        self.addTitleForSend.emit(titleData)

    @pyqtSlot(str)
    def titleSentEmit(self, info: str):
        self.titleSent.emit(info)

    @pyqtSlot(result=str)
    def getInitialData(self):
        return self._initialData

    @pyqtSlot(str)
    def setInitialData(self, value: str):
        self._initialData = value

    initialData = pyqtProperty(str, getInitialData, setInitialData)

    @pyqtSlot(str)
    def openCoverInExplorerEmit(self, path):
        self.openCoverInExplorer.emit(path)

    @pyqtSlot(str)
    def openLinkInBrowserEmit(self, link):
        self.openLinkInBrowser.emit(link)
