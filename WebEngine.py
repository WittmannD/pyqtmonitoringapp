import json
import logging
import os
import sys


from datetime import datetime

from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot, QFile, QUrl, QIODevice, QByteArray, Qt, QCoreApplication, QEvent, QPoint, \
    pyqtSignal
from PyQt5.QtNetwork import QNetworkCookie
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView, QWebEngineProfile, QWebEngineScript

from Backend import Backend
from Controller import Controller

URL = 'https://remanga.org/panel/add-titles/'
CURRENT_DIR = os.path.dirname(__file__)
COOKIES = os.path.join(CURRENT_DIR, 'client/cookies.json')
JS_INJECTION = os.path.join(CURRENT_DIR, 'client/userscripts/host.js')


class WebProfile(QWebEngineProfile):
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/91.0.4472.164 Safari/537.36 OPR/77.0.4054.277'
    WEBCHANNEL_SCRIPT = ':/qtwebchannel/qwebchannel.js'

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        super(WebProfile, self).__init__(name, parent)

    def setCookiesFromFile(self, file):
        with open(file, encoding='utf-8') as f:
            data = json.load(f)
            cookies = self.cookieStore()
            url = QUrl(URL.replace(QUrl(URL).path(), ''))

            for item in data:
                cookie = QNetworkCookie()

                cookie.setDomain(item['domain'])
                cookie.setExpirationDate(datetime.fromtimestamp(item['expires']))
                cookie.setHttpOnly(item['httpOnly'])
                cookie.setSecure(item['secure'])
                cookie.setValue(item['value'].encode('utf-8'))
                cookie.setName(item['name'].encode('utf-8'))
                cookie.setPath(item['path'])

                cookies.setCookie(cookie, url)

    def injectScripts(self, script_list):
        webchannel_file = QFile(self.WEBCHANNEL_SCRIPT)
        name = webchannel_file.fileName()

        if not webchannel_file.open(QIODevice.ReadOnly):
            raise Exception('can\'t load ' + name)

        script = webchannel_file.readAll()

        for path in script_list:
            script_file = QFile(path)

            if not script_file.open(QIODevice.ReadOnly):
                raise Exception('can\'t load ' + path)

            else:
                script.append(script_file.readAll())

        user_script = QWebEngineScript()
        user_script.setName(name)
        user_script.setWorldId(QWebEngineScript.MainWorld)
        user_script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        user_script.setSourceCode(str(script, encoding='utf-8'))

        self.scripts().insert(user_script)

    @staticmethod
    def create(name, cookies_file, scripts=None, parent=None):
        profile = WebProfile(name, parent)
        profile.setHttpUserAgent(WebProfile.USER_AGENT)
        profile.setCookiesFromFile(cookies_file)
        profile.injectScripts(scripts)

        return profile


class WebView(QWebEngineView):

    def __init__(self, *args, **kwargs):
        super(WebView, self).__init__(*args, **kwargs)

        self.controller = Controller()
        self.profile = WebProfile.create('storage', COOKIES, scripts=[JS_INJECTION], parent=self)

    def createPage(self):
        self.setPage(WebPage(self.controller, self.profile, self))

        self.page().load(QUrl(URL))

    def createHomePage(self):
        base_dir = os.path.join(CURRENT_DIR, os.path.normpath(os.getenv('PUBLIC_URL')))

        print(base_dir)
        file_path = os.path.join(base_dir, 'index.html')
        base_url = QUrl.fromLocalFile(os.path.normpath(file_path))

        file = QFile(file_path)
        file.open(QIODevice.ReadOnly)

        self.setPage(WebPage(self.controller, self.profile, self))
        self.page().setHtml(str(file.readAll(), encoding='utf-8'), baseUrl=base_url)
        file.close()


class WebPage(QWebEnginePage):

    def __init__(self, controller, profile, parent):
        super(WebPage, self).__init__(profile, parent)

        self.file = ''
        self.controller = controller
        self.backend = Backend(self)
        self.createChannel()
        self._logger = logging.getLogger(self.__class__.__name__)

    def createChannel(self):
        channel = QWebChannel(self)
        self.setWebChannel(channel)
        channel.registerObjects({'backend': self.backend, 'controller': self.controller})

    def chooseFiles(self, mode, oldFiles, acceptedMimeTypes):
        return [self.file]

    def _loadFinished(self) -> None:
        pass

    def javaScriptConsoleMessage(self, level: QWebEnginePage.JavaScriptConsoleMessageLevel, message: str,
                                 lineNumber: int, sourceID: str) -> None:
        self._logger.info(
            'JS console message\n'
            '    source: %s\n'
            '    [%s] %s\n',
            sourceID,
            lineNumber,
            message
        )


if __name__ == '__main__':
    app = QApplication([])

    web_view = WebView()
    web_view.createPage()
    web_view.show()

    if os.environ.get('DEVTOOLS'):
        dev_view = QWebEngineView()
        web_view.page().setDevToolsPage(dev_view.page())
        dev_view.show()

    sys.exit(app.exec())
