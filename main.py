import logging
import os
import sys

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication

import settings
from Config import Config
from Controller import Controller
from MainWindow import MainWindow
from monitoring.Dispatcher import Dispatcher

try:
    from PyQt5.QtWinExtras import QtWin
    myappid = 'com.mushokutensei.monitoring.app'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)

    QCoreApplication.setOrganizationDomain(myappid)
    QCoreApplication.setOrganizationName('mushokutensei')
    QCoreApplication.setApplicationName('Monitoring Bot v2')
except ImportError:
    pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    config = Config()
    config.load(os.path.join(settings.CONFIG_PATH))

    controller = Controller()

    logging.config.dictConfig(config.property('docs').get('logging'))

    dispatcher = Dispatcher()
    dispatcher.start()

    main_window = MainWindow(config, controller)
    main_window.show()

    if settings.DEVTOOLS:
        dev_view = QWebEngineView()
        main_window.browserWidget.web_views[0].page().setDevToolsPage(dev_view.page())
        dev_view.show()

    app.exec()
    dispatcher.shutdown()
    sys.exit(0)
