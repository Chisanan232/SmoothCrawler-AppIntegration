from typing import List, Iterable
from abc import ABCMeta, abstractmethod

from .format import BaseFile as _BaseFile



class BaseSaver(metaclass=ABCMeta):

    """
    *saver* module be an adapter of the module of module *format*. It could provide APIs
    to others to use and guarantee the features works finely from ruled interface.

    *saver* is responsible of APIs usage compatibility. But it may change to define the
    usage procedure and turn to be a *Builder*, which means these modules would change
    to be Builder Pattern from Adapter Pattern.
    """

    _File: _BaseFile = None

    def __init__(self, file: _BaseFile, file_name: str, mode: str, encoding: str):
        if not isinstance(file, _BaseFile):
            raise TypeError("Parameter *file* should be one of smoothcrawler.persistence.(CSVFormat, XLSXFormat, JSONFormat, XMLFormat, PropertiesFormat).")
        self._File = file

        self._File.file_path = file_name
        self._File.mode = mode
        self._File.encoding = encoding


    def __enter__(self):
        self.open()


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


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
    def open(self) -> None:
        pass


    @abstractmethod
    def write(self, data: List[list]) -> None:
        pass


    @abstractmethod
    def read(self) -> Iterable[Iterable]:
        pass


    @abstractmethod
    def close(self) -> None:
        pass



class FileSaver(BaseSaver):

    def open(self) -> None:
        self._File.open()


    def write(self, data: List[list]) -> None:
        self._File.write(data=data)


    def read(self) -> Iterable[Iterable]:
        _data = self._File.read()
        return _data


    def close(self) -> None:
        self._File.close()

