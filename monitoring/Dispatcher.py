import logging
import sys
import traceback
import json
from typing import List, Dict, Tuple

from PyQt5.QtCore import QObject, pyqtSlot, QJsonValue, QThread, QRunnable, QThreadPool
from asyncqt import QEventLoop
import asyncio
import aiohttp.client_exceptions
import time

from Controller import Controller
from models.models import MonitorDataModel
from monitoring.Monitor import HttpMonitor
from monitoring.handler.DataProcessing import DataProcessing
from utils.utils import jsonToPyObject


class Thread(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Thread, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self._logger = logging.getLogger(self.__class__.__name__)

    @pyqtSlot()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)

        except Exception:
            traceback.print_exc()
            self._logger.exception('Worker error')


async def _run_monitor(monitor: HttpMonitor, is_stopped: asyncio.Event) -> bool:
    def _until_next(last: float) -> float:
        time_took = time.time() - last
        return max(monitor.check_every - time_took, 0)

    while True:
        time_start = time.time()

        try:
            await monitor.check()

        except asyncio.CancelledError:
            break

        except asyncio.TimeoutError:
            continue

        except aiohttp.client_exceptions.ClientOSError:
            monitor.logger.warning('Connection was aborted')
            continue

        except Exception as err:
            monitor.logger.exception('Error executing monitor check')

        await asyncio.sleep(_until_next(last=time_start))

        if is_stopped.is_set():
            return False


class Dispatcher(QObject):
    def __init__(self, parent=None):
        super(Dispatcher, self).__init__(parent)
        self.controller = Controller()
        self.handler = DataProcessing()
        self.threadPool = QThreadPool()

        self.max_tasks = 20
        self.getters: List[List[str, asyncio.Task]] = []
        self.is_stopped = None
        self.queue = None
        self.loop = None

        self.connectSlots()

    @pyqtSlot(str)
    def addMonitor(self, monitorData: str):
        monitorData: MonitorDataModel = jsonToPyObject(monitorData, MonitorDataModel)
        monitor = HttpMonitor(monitorData, self.handler.run, self.loop)

        asyncio.run_coroutine_threadsafe(self.queue.put(monitor), self.loop).result()
        self.controller.commitMonitor.emit(json.dumps(monitorData._asdict()))

    @pyqtSlot(str)
    def removeMonitor(self, uid: str):
        self.cancelTask(uid)

    def connectSlots(self):
        self.controller.addMonitor.connect(self.addMonitor)
        self.controller.removeMonitor.connect(self.removeMonitor)

    async def _work(self, ind: int):
        while True:
            try:
                monitor: HttpMonitor = await self.queue.get()
                self.getters[ind][0] = monitor.uid
                await _run_monitor(monitor, self.is_stopped)

            except asyncio.CancelledError:
                break

    async def run(self):
        self.getters.extend([
            ['', asyncio.create_task(self._work(i))]
            for i in range(self.max_tasks)
        ])
        return await asyncio.gather(*[task for _, task in self.getters])

    def cancelTask(self, uid):
        for _uid, task in self.getters:
            if _uid == uid:
                self.loop.call_soon_threadsafe(task.done)
                self.loop.call_soon_threadsafe(task.cancel)

    def shutdown(self):
        self.is_stopped.set()
        for _uid, task in self.getters:  # exit from worker loop
            self.loop.call_soon_threadsafe(task.done)
            self.loop.call_soon_threadsafe(task.cancel)

        for _uid, task in self.getters:  # exit from getter loop
            self.loop.call_soon_threadsafe(task.cancel)

        self.threadPool.clear()

    def _start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.queue = asyncio.Queue(loop=self.loop)
        self.is_stopped = asyncio.Event(loop=self.loop)
        self.loop.run_until_complete(self.run())

    def start(self):
        thread_worker = Thread(self._start)
        self.threadPool.start(thread_worker)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QPushButton
    from Config import Config
    import json
    config = Config()
    config.load('../config.yml')
    controller = Controller()
    app = QApplication([])
    monitor_d = json.dumps({
        'uid': 'str',
        'name': 'hellow',
        'keyword': 'str',
        'description': 'str',
        'timeout': 12.0,
        'check_every': 12.0,
        'method': 'GET',
        'url': 'http://localhost:8080/get_isbn/12',
        'payload': {}
    })
    btn = QPushButton('click')
    btn.clicked.connect(lambda: controller.addMonitorEmit(monitor_d))

    btn.show()

    dispatcher = Dispatcher()
    dispatcher.start()

    sys.exit(app.exec())
