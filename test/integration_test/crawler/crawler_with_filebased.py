from appintegration.task.filebased import FileBasedTask, CSVTask, XLSXTask, JSONTask, XMLTask, PropertiesTask
from appintegration.crawler import FileBasedCrawler
from appintegration.factory import ApplicationIntegrationFactory
from appintegration.role import CrawlerSource, CrawlerProcessor
from appintegration.url import OPTION_VAR_DATE, API, FileBasedURL

from ...unit_test._utils.file.format import FormatTestSpec
from ..._config import (
    # For testing file path
    Test_CSV_File_Path, Test_XLSX_File_Path, Test_JSON_File_Path, Test_XML_File_Path, Test_PROPERTIES_File_Path,
    # For file IO streaming mode
    Test_Reading_Mode, Test_Writing_Mode, Test_XML_Writing_Mode
)
from .._config import (
    # For testing file path about back to application integration system
    Back_CSV_File_Path, Back_XLSX_File_Path, Back_JSON_File_Path, Back_XML_File_Path, Back_Properties_File_Path
)
from ._components import DataFilePersistenceLayer
from ._spec import CrawlerTestSpec

from typing import Iterable, TypeVar, Generic, cast
from abc import abstractmethod
import pytest
import random
import time
import os


_FileBasedTask = TypeVar("_FileBasedTask", bound=FileBasedTask)


class FileBasedCrawlerTestSpec(CrawlerTestSpec):

    def processor_role(self) -> CrawlerProcessor:
        return CrawlerProcessor(task=self.task(file=self.file_path, mode=self.reading_mode))


    @abstractmethod
    def task(self, file: str, mode: str) -> Generic[_FileBasedTask]:
        """
        One of the **ApplicationIntegrationTask** type --- **FileBasedTask**, it has
        2 options *file* and *mode*.

        :param file: The file path.
        :param mode: The mode to open file streaming.
        :return: An instance of object which is the sub-class of **FileBasedTask**.
        """

        pass


    @property
    @abstractmethod
    def file_path(self) -> str:
        """
        Where the file path to let testing uses.

        :return: A file path which is string type value.
        """

        pass


    @property
    def reading_mode(self) -> str:
        """
        The *mode* to open file streaming to read.

        :return: A string type value.
        """

        return Test_Reading_Mode


    @property
    @abstractmethod
    def writing_mode(self) -> str:
        """
        The *mode* to open file streaming to write data to it.

        :return: A string type value.
        """

        pass


    @property
    @abstractmethod
    def back_file_path(self) -> str:
        """
        Where file path should it saves in process about crawler let result data write back to file.

        :return: A file path which is string type value.
        """

        pass


    @property
    def sleep_time(self) -> int:
        """
        Let crawler to sleep for a while because web server would block the IP address temporarily
        and it would cause fail of running testing. So it needs to sleep several seconds to reduce
        the burdens of web server.

        :return: An integer type value. Unit is *seconds*.
        """

        # Sleep for 8 seconds to reduce the burdens of web site.
        return 8


    @pytest.fixture(scope="class")
    def crawler(self, factory: ApplicationIntegrationFactory) -> FileBasedCrawler:
        return FileBasedCrawler(factory=factory)


    def _chk_result_of_getting_targets(self, _targets: Iterable) -> None:
        assert type(_targets) is list, "It should be an iterable object."
        _chk_ele_is_list = map(lambda a: True if type(a) is list else False, _targets)
        if False in list(_chk_ele_is_list):
            assert False, "It should NOT have any element which type is not list."
        else:
            assert True, "It works finely."


    def _chk_result_of_running(self, _results: Iterable) -> None:
        assert type(_results) is list and len(_results) != 0, "The results of crawling by method *run* should not be empty."
        for _result in _results:
            assert _result["stat"] == "OK", "The state of result should be 'OK'."
            assert "202206" in _result["date"], "The date time in result should be 2022/06/XX."
            assert _result["title"] == "111年06月 2330 台積電           各日成交資訊", "The title should be the pound of Taiwan."
            _fields = ["日期", "成交股數", "成交金額", "開盤價", "最高價", "最低價", "收盤價", "漲跌價差", "成交筆數"]
            assert random.choice(_fields) in _result["fields"], f"The field should contain one of the fields list {_fields}"
            assert type(_result["data"]) is list and len(_result["data"]) != 0, "It should have something data."
            for _data_rows in _result["data"]:
                assert len(_data_rows) == 9, "It should have something data."


    def _chk_result_of_running_and_saving(self, _factory) -> None:
        _persistence_layer = cast(DataFilePersistenceLayer, _factory.persistence_factory)
        _exist = os.path.exists(_persistence_layer.file_path)
        assert _exist is True, f"It should exist a file {_persistence_layer.file_path}."
        os.remove(_persistence_layer.file_path)


    def test_run_and_back_to_middle(self, crawler: FileBasedCrawler) -> None:
        self._prepare_target_data()

        try:
            _targets = crawler.get_target()
            for _target in _targets:
                crawler.run_and_back_to_middle(target=_target)

            _factory = crawler.factory
            self._chk_result_of_running_and_backing_to_middle()
        finally:
            self._final_process()


    def _chk_result_of_running_and_backing_to_middle(self) -> None:
        _exist = os.path.exists(self.back_file_path)
        assert _exist is True, f"It should exist a file {self.back_file_path}."
        os.remove(self.back_file_path)


    def _prepare_target_data(self) -> None:
        _target_url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={" + OPTION_VAR_DATE + "}&stockNo=2330"
        _role = CrawlerSource(task=self.task(file=self.file_path, mode=self.writing_mode))

        _date_urls = FileBasedURL(role=_role, base=_target_url, start="20220601", end="20220603", formatter="yyyymmdd")
        _date_urls.set_http_info(info=API())
        _date_urls.generate()


    def _final_process(self) -> None:
        _exist = os.path.exists(self.file_path)
        assert _exist is True, f"It should exist a file {self.file_path}."

        FormatTestSpec._remove_files(file=self.file_path)

        time.sleep(self.sleep_time)



class TestFileBasedCrawlerWithCSV(FileBasedCrawlerTestSpec):

    def task(self, file: str, mode: str) -> CSVTask:
        return CSVTask(file=file, mode=mode)


    def source_role(self) -> CrawlerSource:
        return CrawlerSource(task=self.task(file=self.back_file_path, mode=self.writing_mode))


    @property
    def file_path(self) -> str:
        return Test_CSV_File_Path


    @property
    def writing_mode(self) -> str:
        return Test_Writing_Mode


    @property
    def back_file_path(self) -> str:
        return Back_CSV_File_Path



class TestFileBasedCrawlerWithXLSX(FileBasedCrawlerTestSpec):

    def task(self, file: str, mode: str) -> XLSXTask:
        return XLSXTask(file=file, mode=mode)


    def source_role(self) -> CrawlerSource:
        return CrawlerSource(task=self.task(file=self.back_file_path, mode=self.writing_mode))


    @property
    def file_path(self) -> str:
        return Test_XLSX_File_Path


    @property
    def writing_mode(self) -> str:
        return Test_Writing_Mode


    @property
    def back_file_path(self) -> str:
        return Back_XLSX_File_Path



class TestFileBasedCrawlerWithJSON(FileBasedCrawlerTestSpec):

    def task(self, file: str, mode: str) -> JSONTask:
        return JSONTask(file=file, mode=mode)


    def source_role(self) -> CrawlerSource:
        return CrawlerSource(task=self.task(file=self.back_file_path, mode=self.writing_mode))


    @property
    def file_path(self) -> str:
        return Test_JSON_File_Path


    @property
    def writing_mode(self) -> str:
        return Test_Writing_Mode


    @property
    def back_file_path(self) -> str:
        return Back_JSON_File_Path



class TestFileBasedCrawlerWithXML(FileBasedCrawlerTestSpec):

    def task(self, file: str, mode: str) -> XMLTask:
        return XMLTask(file=file, mode=mode)


    def source_role(self) -> CrawlerSource:
        return CrawlerSource(task=self.task(file=self.back_file_path, mode=self.writing_mode))


    @property
    def file_path(self) -> str:
        return Test_XML_File_Path


    @property
    def writing_mode(self) -> str:
        return Test_XML_Writing_Mode


    @property
    def back_file_path(self) -> str:
        return Back_XML_File_Path



class TestFileBasedCrawlerWithProperties(FileBasedCrawlerTestSpec):

    def task(self, file: str, mode: str) -> PropertiesTask:
        return PropertiesTask(file=file, mode=mode)


    def source_role(self) -> CrawlerSource:
        return CrawlerSource(task=self.task(file=self.back_file_path, mode=self.writing_mode))


    @property
    def file_path(self) -> str:
        return Test_PROPERTIES_File_Path


    @property
    def writing_mode(self) -> str:
        return Test_Writing_Mode


    @property
    def back_file_path(self) -> str:
        return Back_Properties_File_Path

