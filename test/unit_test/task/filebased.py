from smoothcrawler_appintegration.task.framework import ApplicationIntegrationSourceTask, ApplicationIntegrationProcessorTask
from smoothcrawler_appintegration.task.filebased import CSVTask, XLSXTask, JSONTask, XMLTask, PropertiesTask

from ..._config import (
    # For file paths
    Test_CSV_File_Path,
    Test_XLSX_File_Path,
    Test_JSON_File_Path,
    Test_XML_File_Path,
    Test_PROPERTIES_File_Path,
    # For opening mode of file
    Test_Reading_Mode, Test_Writing_Mode, Test_XML_Writing_Mode
)
from ..._data import Test_Data_List, Test_JSON_Data
from .._utils.file.format import FormatTestSpec
from ._spec import AppIntegrationTaskTestSpec, _AppIntegrationTaskGeneric

from typing import Union, Iterable, Any, Generic
import pytest


_AppIntegrationTask = Union[ApplicationIntegrationSourceTask, ApplicationIntegrationProcessorTask]


class TestCSVTask(AppIntegrationTaskTestSpec):

    """
    Testing for the features *generate* and *acquire* of object **CSVTask**.
    """

    @pytest.fixture(scope="class")
    def task_for_generating(self, task: _AppIntegrationTask) -> CSVTask:
        return CSVTask(file=Test_CSV_File_Path, mode=Test_Writing_Mode)


    @pytest.fixture(scope="class")
    def task_for_acquiring(self, task: _AppIntegrationTask) -> CSVTask:
        return CSVTask(file=Test_CSV_File_Path, mode=Test_Reading_Mode)


    def _testing_data(self) -> Union[Iterable[Iterable], Any]:
        return Test_Data_List


    def _chk_generate_running_result(self, **kwargs) -> None:
        super(TestCSVTask, self)._chk_generate_running_result(file_path=Test_CSV_File_Path)


    def _chk_acquire_running_result(self, **kwargs) -> None:
        _data = kwargs.get("data")
        for index, d in enumerate(_data):
            for ele_d, ele_o in zip(d, Test_Data_List[index]):
                assert str(ele_d) == str(ele_o), "Each values in the data row should be the same."


    def _chk_acquire_final_ps(self, **kwargs) -> None:
        FormatTestSpec._remove_files(file=Test_CSV_File_Path)



class TestXLSXTask(AppIntegrationTaskTestSpec):

    """
    Testing for the features *generate* and *acquire* of object **XLSXTask**.
    """

    @pytest.fixture(scope="class")
    def task(self) -> Generic[_AppIntegrationTaskGeneric]:
        return XLSXTask(file=Test_XLSX_File_Path, mode="")


    def _testing_data(self) -> Union[Iterable[Iterable], Any]:
        return Test_Data_List


    def _chk_generate_running_result(self, **kwargs) -> None:
        super(TestXLSXTask, self)._chk_generate_running_result(file_path=Test_XLSX_File_Path)


    def _chk_acquire_running_result(self, **kwargs) -> None:
        _data = kwargs.get("data")
        for index, d in enumerate(_data):
            for ele_d, ele_o in zip(d, Test_Data_List[index]):
                assert str(ele_d) == str(ele_o), "Each values in the data row should be the same."


    def _chk_acquire_final_ps(self, **kwargs) -> None:
        FormatTestSpec._remove_files(file=Test_XLSX_File_Path)



class TestJSONTask(AppIntegrationTaskTestSpec):

    """
    Testing for the features *generate* and *acquire* of object **JSONTask**.
    """

    @pytest.fixture(scope="class")
    def task_for_generating(self, task: _AppIntegrationTask) -> JSONTask:
        return JSONTask(file=Test_JSON_File_Path, mode=Test_Writing_Mode)


    @pytest.fixture(scope="class")
    def task_for_acquiring(self, task: _AppIntegrationTask) -> JSONTask:
        return JSONTask(file=Test_JSON_File_Path, mode=Test_Reading_Mode)


    def _testing_data(self) -> Union[Iterable[Iterable], Any]:
        return Test_JSON_Data


    def _chk_generate_running_result(self, **kwargs) -> None:
        super(TestJSONTask, self)._chk_generate_running_result(file_path=Test_JSON_File_Path)


    def _chk_acquire_running_result(self, **kwargs) -> None:
        _data = kwargs.get("data")

        assert "data" in _data.keys(), "The key 'data' should be in the JSON format data."
        assert _data["data"] is not None and len(_data["data"]) != 0, "It should has some data row with the key 'data' in JSON format content."
        for index, d in enumerate(_data["data"]):
            for ele_d, ele_o in zip(d, Test_Data_List[index]):
                assert str(ele_d) == str(ele_o), "Each values in the data row should be the same."


    def _chk_acquire_final_ps(self, **kwargs) -> None:
        FormatTestSpec._remove_files(file=Test_JSON_File_Path)



class TestXMLTask(AppIntegrationTaskTestSpec):

    """
    Testing for the features *generate* and *acquire* of object **XMLTask**.
    """

    @pytest.fixture(scope="class")
    def task_for_generating(self, task: _AppIntegrationTask) -> XMLTask:
        return XMLTask(file=Test_XML_File_Path, mode=Test_XML_Writing_Mode)


    @pytest.fixture(scope="class")
    def task_for_acquiring(self, task: _AppIntegrationTask) -> XMLTask:
        return XMLTask(file=Test_XML_File_Path, mode=Test_Reading_Mode)


    def _testing_data(self) -> Union[Iterable[Iterable], Any]:
        return Test_Data_List


    def _chk_generate_running_result(self, **kwargs) -> None:
        super(TestXMLTask, self)._chk_generate_running_result(file_path=Test_XML_File_Path)


    def _chk_acquire_running_result(self, **kwargs) -> None:
        _data = kwargs.get("data")
        for index, d in enumerate(_data):
            for ele_d, ele_o in zip(d, Test_Data_List[index][:len(d)]):
                assert str(ele_d) == str(ele_o), "Each values in the data row should be the same."


    def _chk_acquire_final_ps(self, **kwargs) -> None:
        FormatTestSpec._remove_files(file=Test_XML_File_Path)



class TestPropertiesTask(AppIntegrationTaskTestSpec):

    """
    Testing for the features *generate* and *acquire* of object **PropertiesTask**.
    """

    @pytest.fixture(scope="class")
    def task_for_generating(self, task: _AppIntegrationTask) -> PropertiesTask:
        return PropertiesTask(file=Test_PROPERTIES_File_Path, mode=Test_Writing_Mode)


    @pytest.fixture(scope="class")
    def task_for_acquiring(self, task: _AppIntegrationTask) -> PropertiesTask:
        return PropertiesTask(file=Test_PROPERTIES_File_Path, mode=Test_Reading_Mode)


    def _testing_data(self) -> Union[Iterable[Iterable], Any]:
        return Test_Data_List


    def _chk_generate_running_result(self, **kwargs) -> None:
        super(TestPropertiesTask, self)._chk_generate_running_result(file_path=Test_PROPERTIES_File_Path)


    def _chk_acquire_running_result(self, **kwargs) -> None:
        _data = kwargs.get("data")
        for index, d in enumerate(_data):
            for ele_d, ele_o in zip(d, Test_Data_List[index][:len(d)]):
                assert str(ele_d) == str(ele_o), "Each values in the data row should be the same."


    def _chk_acquire_final_ps(self, **kwargs) -> None:
        FormatTestSpec._remove_files(file=Test_PROPERTIES_File_Path)

