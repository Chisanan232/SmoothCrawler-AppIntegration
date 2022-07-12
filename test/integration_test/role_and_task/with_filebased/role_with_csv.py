from smoothcrawler_appintegration.task.filebased import CSVTask

from ...._config import Test_CSV_File_Path, Test_Reading_Mode, Test_Writing_Mode
from ...._data import Test_Data_List
from .._spec import _AppIntegrationRole
from ._spec import FileBasedTestSpecConfig, SourceWithFileBasedTestSpec, ProcessorWithFileBasedTestSpec

from typing import Iterable, Any, Generic, Union
import pytest



class CSVFileBasedTestSpecConfig(FileBasedTestSpecConfig):

    def file_path(self) -> str:
        return Test_CSV_File_Path


    def data(self) -> Union[Iterable[Iterable], Any]:
        return Test_Data_List



class TestCrawlerSourceWithCSVTask(SourceWithFileBasedTestSpec):

    @property
    def spec_config(self) -> FileBasedTestSpecConfig:
        return CSVFileBasedTestSpecConfig()


    @pytest.fixture(scope="class")
    def task(self) -> Generic[_AppIntegrationRole]:
        _file_path = self.file_path
        return CSVTask(file=_file_path, mode=Test_Writing_Mode)



class TestCrawlerProcessorWithCSVTask(ProcessorWithFileBasedTestSpec):

    @property
    def spec_config(self) -> FileBasedTestSpecConfig:
        return CSVFileBasedTestSpecConfig()


    @pytest.fixture(scope="class")
    def task(self) -> Generic[_AppIntegrationRole]:
        _file_path = self.file_path
        return CSVTask(file=_file_path, mode=Test_Reading_Mode)


    def _chk_running_result(self, **kwargs) -> None:
        _data = kwargs.get("data")

        for index, d in enumerate(_data):
            for ele_d, ele_o in zip(d, Test_Data_List[index]):
                assert str(ele_d) == str(ele_o), "Each values in the data row should be the same."

