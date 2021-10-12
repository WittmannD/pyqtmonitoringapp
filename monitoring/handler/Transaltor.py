import asyncio
import json
import logging
from typing import List, Tuple
from urllib.parse import quote
from html import unescape

import aiohttp

from models.models import TranslatorResponseDataModel, TranslatorRequestDataModel
from settings import GOOGLE_API_KEY


def _format_response(source: str, response_text: str) -> TranslatorResponseDataModel:
    json_response = json.loads(response_text)
    translated_text = json_response['data']['translations'][0]['translatedText']
    return TranslatorResponseDataModel(
        source,
        unescape(translated_text),
        json_response['data']['translations'][0]['detectedSourceLanguage']
    )


class Translator:
    API_KEY = GOOGLE_API_KEY

    def __init__(self, trying_connection=5):
        self.trying_connection = trying_connection
        self._logger = logging.getLogger(self.__class__.__name__)

    def __build_uri(self, source: str, target_language: str) -> str:
        return f'https://translation.googleapis.com/language/translate/v2?q={quote(source)}' \
               f'&target={target_language}&key={self.API_KEY}'

    async def __download_string(self, session, url):
        repeating = 0

        while self.trying_connection > repeating:
            try:
                r = await session.get(url)
                text = await r.text()

                r.raise_for_status()  # This will error if API return 4xx or 5xx status.
                return text

            except aiohttp.ClientConnectionError as e:
                self._logger.warning(
                    'Translator warning\n'
                    '    details: %s\n'
                    '    try number: %s',
                    '    request took: %s seconds',
                    'Connection was dropped before translate was finished',
                    str(e),
                    url,
                    repeating
                )

            except aiohttp.ClientError as e:
                self._logger.warning(
                    'Translator warning\n'
                    '    details: %s\n'
                    '    url: %s\n'
                    '    try number: %s',
                    'Something went wrong. Not a connection error, that was handled',
                    str(e),
                    url,
                    repeating
                )

            finally:
                repeating += 1

    async def __process(self, session, source: str, target_language: str) -> TranslatorResponseDataModel:
        translate_uri = self.__build_uri(source, target_language)
        translated_response_text = await self.__download_string(session, translate_uri)
        response = _format_response(source, translated_response_text)

        return response

    async def translate(self, data: List[TranslatorRequestDataModel]) -> List[TranslatorResponseDataModel]:
        timeout = len(data) * 10

        async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(timeout),
                loop=asyncio.get_event_loop()
        ) as session:
            result: List[TranslatorResponseDataModel] = []
            result.extend(
                await asyncio.gather(*[self.__process(session, item.source, item.target_language) for item in data])
            )
            return result
