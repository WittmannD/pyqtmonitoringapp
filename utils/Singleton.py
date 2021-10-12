try:
    from PyQt5.QtCore import pyqtWrapperType
except ImportError:
    from PyQt5.sip import wrappertype as pyqtWrapperType


class Singleton(pyqtWrapperType, type):
    _instances = {}

    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]
