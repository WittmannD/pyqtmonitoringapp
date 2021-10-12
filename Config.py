from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal
from utils.Singleton import Singleton
import yaml


class Config(QObject, metaclass=Singleton):
    updated = pyqtSignal()
    LOADER = yaml.CLoader
    DUMPER = yaml.CDumper

    def __init__(self, docs=None, parent=None):
        super(Config, self).__init__(parent)

        if docs is None:
            docs = dict()

        self._docs = docs
        self.load = self._load

    def _load(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            docs = yaml.load(f, self.LOADER)
            self.docs = docs

    @classmethod
    def load(cls, path):
        with open(path, 'r', encoding='utf-8') as f:
            docs = yaml.load(f, cls.LOADER)
            return Config(docs=docs)

    def getDocs(self):
        return self._docs

    def setDocs(self, docs):
        self._docs = docs
        self.updated.emit()

    docs = pyqtProperty('QVariantMap', getDocs, setDocs, notify=updated)


if __name__ == '__main__':
    cof = Config.load('config.yml')
