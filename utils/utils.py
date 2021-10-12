import json
from typing import ClassVar, Type, TypeVar, NamedTuple


def jsonToPyObject(jsonData: str, dataModel: ClassVar):
    data = json.loads(jsonData)
    return dataModel(**data)
