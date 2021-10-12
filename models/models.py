from typing import NamedTuple, Dict, Any, List


class MonitorDataModel(NamedTuple):
    uid: str
    name: str
    keyword: str
    description: str
    timeout: float
    check_every: float
    method: str
    url: str
    payload: Dict[str, Any]


class TranslatorResponseDataModel(NamedTuple):
    source: str
    translated: str
    detected_language: str


class TranslatorRequestDataModel(NamedTuple):
    source: str
    target_language: str


class TitleDescriptionDataModel(NamedTuple):
    input_date: str
    publish_predate: str
    publisher: str
    form_detail: str


class PreparedTitleDataModel(NamedTuple):
    uid: str
    rus_title: str
    eng_title: str
    kor_title: str
    cover: str
    isbn: str
    timestamp: float
    keyword: str
    description: TitleDescriptionDataModel
