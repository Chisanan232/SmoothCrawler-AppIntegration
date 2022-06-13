from appintegration._utils.file.format import (
    BaseFile, JSONFormat, CSVFormat, XLSXFormat, XMLFormat, PropertiesFormat
)

from ._data import Test_Data_List, Test_JSON_Data

from pathlib import Path
from typing import List, Iterable, TypeVar, Union, Generic
from abc import ABCMeta, abstractmethod
import traceback
import pytest
import os


_BaseFile = TypeVar("_BaseFile", bound=BaseFile)

Test_CSV_File_Path: str = str(Path("./for_testing.csv"))
Test_XLSX_File_Path: str = str(Path("./for_testing.xlsx"))
Test_JSON_File_Path: str = str(Path("./for_testing.json"))
Test_XML_File_Path: str = str(Path("./for_testing.xml"))
Test_PROPERTIES_File_Path: str = str(Path("./for_testing.properties"))

Test_Writing_Mode: str = "a+"
Test_Reading_Mode: str = "r"

Run_Procedure_List: List[str] = []
Run_Result_Data_List = []


class FormatTestSpec(metaclass=ABCMeta):

    """
    Spec of testing items about module *appintegration._utils.file.format*
    """

    @abstractmethod
    @pytest.fixture(scope="class")
    def file_format(self) -> Generic[_BaseFile]:
        """
        Which object should this class would test for.

        :return: An instance of BaseFile type sub-class object.
        """

        pass


    @abstractmethod
    def test_write(self, file_format: Generic[_BaseFile]) -> None:
        """
        Test for writing feature.

        :param file_format: The instance of function *file_format* return value in current class.
        :return: None
        """

        pass


    @abstractmethod
    def test_read(self, file_format: Generic[_BaseFile]) -> None:
        """
        Test for reading feature.

        :param file_format: The instance of function *file_format* return value in current class.
        :return: None
        """

        pass


    def _writing_process(self, _file_format: BaseFile, _file_path: str, _data: Iterable[Iterable]) -> None:
        """
        Run the truly implementation of saving file process. It would also check the running result
        to check it whether be correct or not finally.

        :param _file_format: The instance of function *file_format* return value in current class.
        :param _file_path: File path.
        :param _data: The data it saves.
        :return: None
        """

        try:
            _file_format.file_path = _file_path
            _file_format.mode = "a+"
            _file_format.encoding = "UTF-8"
            _file_format.open()
            _file_format.write(data=_data)
            _file_format.close()
        except ValueError as e:
            raise e
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert True, "It work finely!"

        self._writing_feature_expected_result(_file_format=_file_format, _file_path=_file_path)


    def _writing_feature_expected_result(self, _file_format: BaseFile, _file_path: str) -> None:
        """
        Check the final running result whether is correct or not at writing process.

        :param _file_format: The instance of function *file_format* return value in current class.
        :param _file_path: File path.
        :return: None
        """

        assert _file_format.file_path == _file_path, f"It should be '{_file_format.file_path}' we set."
        assert _file_format.mode == "a+", f"It should be '{_file_format.mode}' we set."
        assert _file_format.encoding == "UTF-8", f"It should be '{_file_format.encoding}' we set."

        _exist_file = os.path.exists(_file_path)
        assert _exist_file is True, "It should exist a file."


    def _reading_process(self, _file_format: BaseFile, _file_path: str) -> None:
        """
        Run the truly implementation of reading file process. It would also check the running result
        to check it whether be correct or not finally.

        :param _file_format: The instance of function *file_format* return value in current class.
        :param _file_path: File path.
        :return: None
        """

        try:
            _file_format.file_path = _file_path
            _file_format.mode = "r"
            _file_format.encoding = "UTF-8"
            _file_format.open()
            _data = _file_format.read()
            _file_format.close()
        except ValueError as e:
            raise e
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert True, "It work finely!"

        self._reading_feature_expected_result(_file_format=_file_format, _file_path=_file_path, _data=_data)


    def _reading_feature_expected_result(self, _file_format: BaseFile, _file_path: str, _data: Iterable[Iterable]) -> None:
        """
        Check the final running result whether is correct or not at reading process.

        :param _file_format: The instance of function *file_format* return value in current class.
        :param _file_path: File path.
        :param _data: The data which it gets via reading the file.
        :return: None
        """

        assert _file_format.file_path == _file_path, f"It should be '{_file_format.file_path}' we set."
        assert _file_format.mode == "r", f"It should be '{_file_format.mode}' we set."
        assert _file_format.encoding == "UTF-8", f"It should be '{_file_format.encoding}' we set."


    @staticmethod
    def _remove_files(file: Union[str, list]) -> None:
        """
        Remove the testing files. This process should be run finally.

        :return: None
        """

        if type(file) is str:
            os.remove(file)
        elif type(file) is list:
            os.remove(file)
        else:
            raise TypeError("The data type of option *file* should be str or list.")



class TestCSVFormat(FormatTestSpec):

    @pytest.fixture(scope="class")
    def file_format(self) -> CSVFormat:
        return CSVFormat()


    def test_write(self, file_format: CSVFormat) -> None:
        self._writing_process(_file_format=file_format, _file_path=Test_CSV_File_Path, _data=Test_Data_List)


    def test_read(self, file_format: CSVFormat) -> None:
        self._reading_process(_file_format=file_format, _file_path=Test_CSV_File_Path)
        FormatTestSpec._remove_files(file=Test_CSV_File_Path)


    def _reading_feature_expected_result(self, _file_format: BaseFile, _file_path: str, _data: Iterable[Iterable]) -> None:
        super(TestCSVFormat, self)._reading_feature_expected_result(_file_format=_file_format, _file_path=_file_path, _data=_data)

        for index, d in enumerate(_data):
            for ele_d, ele_o in zip(d, Test_Data_List[index]):
                assert str(ele_d) == str(ele_o), "Each values in the data row should be the same."



class TestXLSXFormat(FormatTestSpec):

    @pytest.fixture(scope="class")
    def file_format(self) -> XLSXFormat:
        return XLSXFormat()


    def test_write(self, file_format: XLSXFormat) -> None:
        self._writing_process(_file_format=file_format, _file_path=Test_XLSX_File_Path, _data=Test_Data_List)


    def test_read(self, file_format: XLSXFormat) -> None:
        self._reading_process(_file_format=file_format, _file_path=Test_XLSX_File_Path)
        FormatTestSpec._remove_files(file=Test_XLSX_File_Path)


    def _reading_feature_expected_result(self, _file_format: BaseFile, _file_path: str, _data: Iterable[Iterable]) -> None:
        super(TestXLSXFormat, self)._reading_feature_expected_result(_file_format=_file_format, _file_path=_file_path, _data=_data)

        for index, d in enumerate(_data):
            for ele_d, ele_o in zip(d, Test_Data_List[index]):
                assert str(ele_d) == str(ele_o), "Each values in the data row should be the same."



class TestJSONFormat(FormatTestSpec):

    @pytest.fixture(scope="class")
    def file_format(self) -> JSONFormat:
        return JSONFormat()


    def test_write(self, file_format: JSONFormat) -> None:
        self._writing_process(_file_format=file_format, _file_path=Test_JSON_File_Path, _data=Test_JSON_Data)


    def test_read(self, file_format: JSONFormat) -> None:
        self._reading_process(_file_format=file_format, _file_path=Test_JSON_File_Path)
        FormatTestSpec._remove_files(file=Test_JSON_File_Path)


    def _reading_feature_expected_result(self, _file_format: BaseFile, _file_path: str, _data: Iterable[Iterable]) -> None:
        super(TestJSONFormat, self)._reading_feature_expected_result(_file_format=_file_format, _file_path=_file_path, _data=_data)

        assert "data" in _data.keys(), "The key 'data' should be in the JSON format data."
        assert _data["data"] is not None and len(_data["data"]) != 0, "It should has some data row with the key 'data' in JSON format content."
        for index, d in enumerate(_data["data"]):
            for ele_d, ele_o in zip(d, Test_Data_List[index]):
                assert str(ele_d) == str(ele_o), "Each values in the data row should be the same."

