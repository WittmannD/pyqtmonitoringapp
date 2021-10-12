import asyncio
import json
import logging.config
import os
import subprocess
import sys
import queue
import webbrowser
from typing import List, Optional

from PyQt5.QtGui import QIcon
from aiohttp import ClientSession, ClientTimeout

import settings
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QTabWidget, QTabBar
from PyQt5.QtWebEngineWidgets import QWebEngineView

from Config import Config
from Controller import Controller
from WebEngine import WebView
from models.models import MonitorDataModel, PreparedTitleDataModel
from monitoring.Dispatcher import Dispatcher

CURRENT_DIR = os.path.dirname(__file__)


class BrowserWidget(QTabWidget):

    def __init__(self, parent=None):
        super(BrowserWidget, self).__init__(parent)

        self.controller = Controller()
        self.web_views = []

        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)

        self.createHomeTab()
        self.tabBar().setTabButton(0, QTabBar.RightSide, None)

    def addTab(self, title):
        web_view = WebView()
        web_view.createPage()

        self.web_views.append(web_view)

        return super(BrowserWidget, self).addTab(web_view, title)

    def createHomeTab(self):
        web_view = WebView()
        web_view.createHomePage()

        self.web_views.append(web_view)
        return super(BrowserWidget, self).addTab(web_view, 'Home')

    def closeTab(self, currentIndex):
        currentQWidget = self.widget(currentIndex)
        currentQWidget.deleteLater()
        self.removeTab(currentIndex)
        self.web_views.pop(currentIndex).page().deleteLater()
        self.controller.commitTab.emit(False)


class MainWindow(QMainWindow):
    awidth = 1280
    aheight = 720

    def __init__(self, config, controller, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.config = config
        self.controller = controller
        self.titlesForSend: queue.Queue[PreparedTitleDataModel] = queue.Queue(0)
        self.titleInProcess: Optional[PreparedTitleDataModel] = None
        self.inProcess: bool = False
        self.autoMode: bool = False
        self.tab_iter = None

        self.setInitialData()
        self.centralWidget = QWidget()
        self.centralLayout = QVBoxLayout()
        self.browserWidget = BrowserWidget()
        self.setFocusPolicy(Qt.StrongFocus)
        self.initUi()

    def initUi(self):
        self.setWindowIcon(QIcon('app.ico'))
        self.setWindowTitle('Monitoring Bot v2')
        self.setMinimumWidth(460)

        desktopRect = QApplication.desktop().availableGeometry(self)
        center = desktopRect.center()
        self.setGeometry(center.x() - self.awidth // 2, center.y() - self.aheight // 2, self.awidth, self.aheight)

        self.centralLayout.setContentsMargins(0, 0, 0, 0)
        self.centralLayout.addWidget(self.browserWidget)
        self.centralWidget.setLayout(self.centralLayout)
        self.setCentralWidget(self.centralWidget)

        self.connectSlots()

    def nextTab(self):
        try:
            i = next(self.tab_iter)

            self.browserWidget.addTab('Form {}'.format(i))
            self.browserWidget.setCurrentIndex(i)

        except StopIteration:
            self.browserWidget.setCurrentIndex(0)

    def processTitle(self):
        if not self.inProcess:
            self.setFocus()
            self.showNormal()
            self.inProcess = True

            if self.browserWidget.count() < 2:  # if browser widget have no tab left dynamically add it
                self._createTabs(1)
                return

            try:
                self.titleInProcess = titleData = self.titlesForSend.get_nowait()
                index = 1

                self.browserWidget.setCurrentIndex(index)
                self.browserWidget.web_views[index].page().file = titleData.cover
                self.controller.completeAndSend.emit(json.dumps(titleData._asdict()))

            except queue.Empty:
                self.browserWidget.setCurrentIndex(0)
                self.inProcess = False
                self.titleInProcess = None

    @pyqtSlot()
    def _tabReady(self):
        self.controller.commitTab.emit(True)

        if self.inProcess:  # process title again after dynamically added tab
            self.inProcess = False
            self.processTitle()
            return

        self.nextTab()

    @pyqtSlot(str)
    def _titleSent(self, info):
        sentTitle = self.titleInProcess
        if sentTitle is not None:
            self.controller.setTitleStatus.emit(json.dumps([
                sentTitle.uid,
                json.loads(info)
            ]))
            self.browserWidget.closeTab(1)

        if self.inProcess:
            self.inProcess = False
            self.processTitle()

    @pyqtSlot(int)
    def _createTabs(self, tab_count):
        tab_count = tab_count or 1
        tab_range = (
            self.browserWidget.count(),
            self.browserWidget.count() + tab_count
        )
        self.tab_iter = iter(range(*tab_range))
        self.nextTab()

    @pyqtSlot(str)
    def _addTitleForSend(self, titleData: str):
        initiator, titleData = json.loads(titleData)
        titleData = PreparedTitleDataModel(**titleData)

        if initiator == 'app' and not self.autoMode:
            return

        self.titlesForSend.put_nowait(titleData)  # add title to queue
        self.processTitle()  # process title

    @pyqtSlot(bool)
    def _changeAutoMode(self, state: bool):
        if state:
            self.inProcess = False
            self.titlesForSend.queue.clear()

        self.autoMode = state

    @pyqtSlot(str)
    def _openCoverInExplorer(self, path):
        path = os.path.normpath(path)
        subprocess.Popen(r'explorer /select, "{}"'.format(path))

    @pyqtSlot(str)
    def _openLinkInBrowser(self, link):
        webbrowser.open(link)

    def connectSlots(self):
        self.controller.tabReady.connect(self._tabReady)
        self.controller.createTabs.connect(self._createTabs)
        self.controller.addTitleForSend.connect(self._addTitleForSend)
        self.controller.changeAutoMode.connect(self._changeAutoMode)
        self.controller.openCoverInExplorer.connect(self._openCoverInExplorer)
        self.controller.openLinkInBrowser.connect(self._openLinkInBrowser)
        self.controller.titleSent.connect(self._titleSent)

    def setInitialData(self):
        initialData = {
            'monitors': self.config.property('docs').get('monitoring').get('monitors')
        }

        self.controller.setInitialData(json.dumps(initialData))

