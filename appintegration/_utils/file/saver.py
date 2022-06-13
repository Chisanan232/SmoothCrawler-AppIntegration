from typing import List, Iterable
from abc import ABCMeta, abstractmethod

from .format import BaseFile as _BaseFile



class BaseSaver(metaclass=ABCMeta):

    _File: _BaseFile = None

    def __init__(self, file: _BaseFile, file_name: str, mode: str, encoding: str):
        if not isinstance(file, _BaseFile):
            raise TypeError("Parameter *file* should be one of smoothcrawler.persistence.(CSVFormat, XLSXFormat, JSONFormat, XMLFormat, PropertiesFormat).")
        self._File = file

        self._File.file_path = file_name
        self._File.mode = mode
        self._File.encoding = encoding


    @property
    def file_path(self) -> str:
        return self._File.file_path


    @property
    def mode(self) -> str:
        return self._File.mode


    @property
    def encoding(self) -> str:
        return self._File.encoding


    @abstractmethod
    def write(self, data: List[list]) -> None:
        pass


    @abstractmethod
    def read(self) -> Iterable[Iterable]:
        pass



class FileSaver(BaseSaver):

    def write(self, data: List[list]) -> None:
        self._File.open()
        self._File.write(data=data)
        self._File.close()


    def read(self) -> Iterable[Iterable]:
        self._File.open()
        _data = self._File.read()
        self._File.close()
        return _data

