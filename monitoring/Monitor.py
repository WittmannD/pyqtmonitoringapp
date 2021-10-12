import logging
import asyncio
import time
from typing import Callable

from aiohttp import ClientSession, ClientTimeout

from models.models import MonitorDataModel


class Monitor:

    def __init__(self, check_every: float) -> None:
        self.check_every = check_every
        self.logger = logging.getLogger(self.__class__.__name__)

    async def check(self) -> None:
        raise NotImplementedError()


class HttpMonitor(Monitor):

    def __init__(self, monitorData: MonitorDataModel, callback: Callable, loop) -> None:
        self.uid = monitorData.uid
        self._url = monitorData.url
        self._timeout = monitorData.timeout
        self._payload = monitorData.payload
        self._description = monitorData.description
        self._method = monitorData.method

        self.callback = callback
        self.loop = loop

        super().__init__(check_every=monitorData.check_every)

    async def check(self) -> None:
        time_start = time.time()
        response_json = {}

        async with ClientSession(timeout=ClientTimeout(self._timeout), loop=self.loop) as session:
            async with session.request(method=self._method, url=self._url, data=self._payload) as response:
                response_json.update(await response.json())

        time_end = time.time()
        time_took = time_end - time_start

        self.logger.info(
            'Check\n'
            '    [%s] %s\n'
            '    description: %s\n'
            '    content length: %s\n'
            '    request took: %s seconds',

            response.status,
            self._url,
            self._description,
            response.content_length,
            round(time_took, 3)
        )

        self.callback(response_json)
