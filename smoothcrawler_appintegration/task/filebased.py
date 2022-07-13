from typing import List, Iterable, Any, Optional, TypeVar, Generic
from abc import ABC, abstractmethod

try:
    import configparser
except ImportError:
    pass

from .._utils.file.format import (
    BaseFile as _BaseFile,
    CSVFormat as _CSVFormat,
    XLSXFormat as _XLSXFormat,
    JSONFormat as _JSONFormat,
    XMLFormat as _XMLFormat,
    PropertiesFormat as _PropertiesFormat
)
from .._utils.file.saver import BaseSaver as _BaseSaver, FileSaver as _FileSaver
from .framework import (
    ApplicationIntegrationSourceTask as _SourceTask,
    ApplicationIntegrationProcessorTask as _ProcessorTask
)


_BaseFileType = TypeVar("_BaseFileType", bound=_BaseFile)
_BaseSaverType = TypeVar("_BaseSaverType", bound=_BaseSaver)


class _BaseFileBasedTask(_SourceTask, _ProcessorTask):

    _FileSaver: _BaseSaverType

    def __init__(self, file: str, mode: str, encoding: str = "utf-8"):
        self._file = file
        self._mode = mode
        self._encoding = encoding

        _file_format = self._init_file_format()
        self._FileSaver = self._init_file_saver(file_format=_file_format)


    def __enter__(self):
        self.init()


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


    @abstractmethod
    def _init_file_format(self) -> Generic[_BaseFileType]:
        pass


    @abstractmethod
    def _init_file_saver(self, file_format: _BaseFileType) -> Generic[_BaseSaverType]:
        pass


    def generate(self, data: Iterable[Iterable]) -> Optional[Any]:
        return self.write(data=data)


    def acquire(self) -> Optional[Any]:
        return self.read()


    @abstractmethod
    def write(self, data: Iterable[Iterable]) -> Optional[Any]:
        pass


    @abstractmethod
    def read(self) -> Optional[Any]:
        pass



class FileBasedTask(_BaseFileBasedTask, ABC):

    def _init_file_saver(self, file_format: _BaseFileType) -> Generic[_BaseSaverType]:
        return _FileSaver(file=file_format, file_name=self._file, mode=self._mode, encoding=self._encoding)


    def init(self) -> Any:
        self._FileSaver.open()


    def write(self, data: List[list]) -> None:
        self._FileSaver.write(data=data)


    def read(self) -> Iterable[Iterable]:
        return self._FileSaver.read()


    def close(self) -> None:
        self._FileSaver.close()



class CSVTask(FileBasedTask):

    def _init_file_format(self) -> Generic[_BaseFileType]:
        return _CSVFormat()



class XLSXTask(FileBasedTask):

    def _init_file_format(self) -> Generic[_BaseFileType]:
        return _XLSXFormat()



class JSONTask(FileBasedTask):

    def _init_file_format(self) -> Generic[_BaseFileType]:
        return _JSONFormat()



class XMLTask(FileBasedTask):

    def _init_file_format(self) -> Generic[_BaseFileType]:
        return _XMLFormat()



class PropertiesTask(FileBasedTask):

    def _init_file_format(self) -> Generic[_BaseFileType]:
        return _PropertiesFormat()

