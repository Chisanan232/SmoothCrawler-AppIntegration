from smoothcrawler_appintegration.task.filebased import JSONTask

from ...._config import Test_JSON_File_Path, Test_Reading_Mode, Test_Writing_Mode
from ...._data import Test_JSON_Data, Test_Data_List
from .._spec import _AppIntegrationRole
from ._spec import FileBasedTestSpecConfig, SourceWithFileBasedTestSpec, ProcessorWithFileBasedTestSpec

from typing import Iterable, Any, Generic, Union
import pytest



class JSONFileBasedTestSpecConfig(FileBasedTestSpecConfig):

    def file_path(self) -> str:
        return Test_JSON_File_Path


    def data(self) -> Union[Iterable[Iterable], Any]:
        return Test_JSON_Data



class TestCrawlerSourceWithJSONTask(SourceWithFileBasedTestSpec):

    @property
    def spec_config(self) -> FileBasedTestSpecConfig:
        return JSONFileBasedTestSpecConfig()


    @pytest.fixture(scope="class")
    def task(self) -> Generic[_AppIntegrationRole]:
        _file_path = self.file_path
        return JSONTask(file=_file_path, mode=Test_Writing_Mode)



class TestCrawlerProcessorWithJSONTask(ProcessorWithFileBasedTestSpec):

    @property
    def spec_config(self) -> FileBasedTestSpecConfig:
        return JSONFileBasedTestSpecConfig()


    @pytest.fixture(scope="class")
    def task(self) -> Generic[_AppIntegrationRole]:
        _file_path = self.file_path
        return JSONTask(file=_file_path, mode=Test_Reading_Mode)


    def _chk_running_result(self, **kwargs) -> None:
        _data = kwargs.get("data")

        assert "data" in _data.keys(), "The key 'data' should be in the JSON format data."
        assert _data["data"] is not None and len(_data["data"]) != 0, "It should has some data row with the key 'data' in JSON format content."
        for index, d in enumerate(_data["data"]):
            for ele_d, ele_o in zip(d, Test_Data_List[index]):
                assert str(ele_d) == str(ele_o), "Each values in the data row should be the same."

