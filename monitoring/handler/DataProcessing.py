import asyncio
import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Iterable
from uuid import uuid4

import aiofiles
import aiohttp
from PyQt5.QtCore import QObject, QUrl
from aiohttp import ClientSession

from Config import Config
from Controller import Controller
from models.models import TranslatorRequestDataModel, TitleDescriptionDataModel, PreparedTitleDataModel
from settings import ASSETS_PATH, DOWNLOAD_COVERS, PUBLIC_URL, ROOT
from monitoring.handler.Transaltor import Translator
from utils.Singleton import Singleton

translator = Translator()
config = Config()


def _find_by_isbn(data: Iterable, isbn_set: Iterable) -> list:
    return list(filter(lambda o: o['EA_ISBN'] in isbn_set, data))


def _prepare_isbn(data: Iterable) -> set:
    return set(item['EA_ISBN'] for item in data)


async def _translate(data: dict):
    title = data['TITLE']

    blacklist = config.property('docs').get('blacklist')
    regex = r'(?:\(|\[)?\s?(' + r'|'.join(map(lambda o: '({})'.format(o), blacklist)) + r')\s?(?:\)|\])?'

    title = re.sub(regex, '', title)

    translated = await translator.translate([
        TranslatorRequestDataModel(source=title, target_language='en'),
        TranslatorRequestDataModel(source=title, target_language='ru')
    ])

    return dict(
        kor_title=translated[0].source,
        eng_title=translated[0].translated,
        rus_title=translated[1].translated
    )


async def _download_image(url):
    if not url or not DOWNLOAD_COVERS:
        path = os.path.join(ASSETS_PATH, 'cover.jpg')
        return path

    try:
        filename = url.split('/')[-1]
        path = os.path.join(ASSETS_PATH, filename)

        async with ClientSession(timeout=config.property('docs').image_download_timeout) as session:
            async with session.request(method='GET', url=url) as response:
                if response.status == 200:
                    f = await aiofiles.open(path, mode='wb')
                    await f.write(await response.read())
                    await f.close()

                else:
                    raise Exception()

    except Exception:
        path = os.path.join(ASSETS_PATH, 'cover.jpg')
        return QUrl.fromLocalFile(os.path.abspath(path)).toString()

    return QUrl.fromLocalFile(os.path.abspath(path)).toString()


class DataProcessing(QObject, metaclass=Singleton):
    storage = dict()

    def __init__(self, parent=None):
        super(DataProcessing, self).__init__(parent)
        self.controller = Controller()
        self._logger = logging.getLogger(self.__class__.__name__)

    async def handler(self, data: dict, keyword: str):
        try:
            translate_task = asyncio.create_task(_translate(data))
            download_image_task = asyncio.create_task(_download_image(data['TITLE_URL']))

            translated_data, image_path = await asyncio.gather(translate_task, download_image_task)

            timestamp = datetime.timestamp(datetime.now())

            typesOfFormDetails = {u'기타': 'OTHER', 'EPUB': 'EPUB', 'PDF': 'PDF'}

            title = PreparedTitleDataModel(
                uid=str(uuid4()),
                **translated_data,
                cover=image_path,
                isbn=data['EA_ISBN'],
                timestamp=timestamp,
                keyword=keyword,
                description=TitleDescriptionDataModel(
                    input_date=data['INPUT_DATE'],
                    publish_predate=data['PUBLISH_PREDATE'],
                    publisher=data['PUBLISHER'],
                    form_detail=typesOfFormDetails.get(data['FORM_DETAIL'], 'UNKNOWN')
                )
            )

            self.controller.addTitleForSend.emit(json.dumps(['app', title._asdict()]))
            self.controller.commitTitle.emit(json.dumps(title._asdict()))

        except Exception as err:
            self._logger.exception(str(err))

    def run(self, data) -> None:
        keyword = data['responseHeader']['params']['q']
        docs: list = data['response']['docs']

        new_isbn = _prepare_isbn(docs)
        stored = self.storage.setdefault(keyword, set())
        existing_isbn = new_isbn.difference(stored)

        if existing_isbn:
            if not stored:
                stored.update(new_isbn)
                return

            stored.update(new_isbn)

            new_data = _find_by_isbn(docs, existing_isbn)

            asyncio.gather(*[self.handler(item, keyword) for item in new_data])

