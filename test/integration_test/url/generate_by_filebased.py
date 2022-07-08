from appintegration.task.filebased import FileBasedTask
from appintegration.task import (
    # For file based application integration
    CSVTask, XLSXTask, JSONTask, XMLTask, PropertiesTask
)
from appintegration.role import CrawlerSource
from appintegration.url import OPTION_VAR_DATE, API, FileBasedURL

from ...unit_test._utils.file.format import FormatTestSpec
from ..._config import (
    # For file path
    Test_CSV_File_Path, Test_XLSX_File_Path, Test_JSON_File_Path, Test_XML_File_Path, Test_PROPERTIES_File_Path,
    # For mode about file IO stream
    Test_Writing_Mode, Test_XML_Writing_Mode
)
from ._spec import ApplicationIntegrationURLTestSpec

from typing import Iterable, TypeVar, Generic
from abc import ABC, abstractmethod
import pytest
import os


_FileBasedTask = TypeVar("_FileBasedTask", bound=FileBasedTask)


class FileBasedURLTestSpec(ApplicationIntegrationURLTestSpec, ABC):

    @pytest.fixture(scope="class")
    def url(self) -> FileBasedURL:
        _target_url = "http:www.test.com?date={" + OPTION_VAR_DATE + "}"
        _role = self.role(task=self.task())

        _date_urls = FileBasedURL(role=_role, base=_target_url, start="20220601", end="20220603", formatter="yyyymmdd")
        _date_urls.set_http_info(info=API())

        return _date_urls


    @property
    @abstractmethod
    def file_path(self) -> str:
        pass


    def role(self, task: _FileBasedTask) -> CrawlerSource:
        return CrawlerSource(task=task)


    @abstractmethod
    def task(self) -> Generic[_FileBasedTask]:
        pass


    def _chk_format_data_running_result(self, urls: Iterable[Iterable]) -> None:
        assert type(urls) is list, ""
        for _url in urls:
            assert type(_url) is list, ""


    def _chk_generate_running_result(self, url_inst: FileBasedURL) -> None:
        _exist = os.path.exists(self.file_path)
        assert _exist is True, f"It should exist a file {self.file_path}."

        FormatTestSpec._remove_files(file=self.file_path)



class TestFileBasedURLWithCSV(FileBasedURLTestSpec):

    def task(self) -> CSVTask:
        return CSVTask(file=self.file_path, mode=Test_Writing_Mode)


    @property
    def file_path(self) -> str:
        return Test_CSV_File_Path



class TestFileBasedURLWithXLSX(FileBasedURLTestSpec):

    def task(self) -> XLSXTask:
        return XLSXTask(file=self.file_path, mode=Test_Writing_Mode)


    @property
    def file_path(self) -> str:
        return Test_XLSX_File_Path



class TestFileBasedURLWithJSON(FileBasedURLTestSpec):

    def task(self) -> JSONTask:
        return JSONTask(file=self.file_path, mode=Test_Writing_Mode)


    @property
    def file_path(self) -> str:
        return Test_JSON_File_Path



class TestFileBasedURLWithXML(FileBasedURLTestSpec):

    def task(self) -> XMLTask:
        return XMLTask(file=self.file_path, mode=Test_XML_Writing_Mode)


    @property
    def file_path(self) -> str:
        return Test_XML_File_Path



class TestFileBasedURLWithProperties(FileBasedURLTestSpec):

    def task(self) -> PropertiesTask:
        return PropertiesTask(file=self.file_path, mode=Test_Writing_Mode)


    @property
    def file_path(self) -> str:
        return Test_PROPERTIES_File_Path

