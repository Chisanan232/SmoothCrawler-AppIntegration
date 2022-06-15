from appintegration._utils.file.format import File
from appintegration._utils.file.saver import BaseSaver, FileSaver

from ..._data import Test_Data_List

from typing import List, Iterable, TypeVar, Generic
from abc import ABCMeta, abstractmethod
import traceback
import pytest


_BaseSaver = TypeVar("_BaseSaver", bound=BaseSaver)

Open_Process: bool = False
Read_Process: bool = False
Write_Process: bool = False
Close_Process: bool = False
Saver_Process: List[str] = []
Writing_Data: List[str] = []

_File_Name: str = "test_file_name"
_Mode: str = "a+"
_Encoding: str = "UTF-8"


def reset_flag() -> None:
    global Open_Process, Read_Process, Write_Process, Close_Process, Saver_Process
    Open_Process = False
    Read_Process = False
    Write_Process = False
    Close_Process = False
    Saver_Process.clear()


class _SpyFileFormat(File):

    def open(self) -> None:
        global Open_Process
        Open_Process = True
        Saver_Process.append("open")


    def write(self, data: Iterable[Iterable]) -> None:
        global Write_Process
        Write_Process = True
        Saver_Process.append("write")


    def read(self, *args, **kwargs) -> Iterable[Iterable]:
        global Read_Process
        Read_Process = True
        Saver_Process.append("read")
        return Writing_Data


    def close(self) -> None:
        global Close_Process
        Close_Process = True
        Saver_Process.append("close")



class SaverTestSpec(metaclass=ABCMeta):

    """
    Spec of testing items about module *appintegration._utils.file.saver*
    """

    @abstractmethod
    @pytest.fixture(scope="class")
    def saver(self) -> Generic[_BaseSaver]:
        """
        Which object should this class would test for.

        :return: An instance of BaseSaver type sub-class object.
        """

        pass


    @abstractmethod
    def test_writing_procedure(self, saver: _BaseSaver) -> None:
        """
        Test for the procedure of writing data as a specific file format.

        :return: None
        """

        pass


    @abstractmethod
    def test_reading_procedure(self, saver: _BaseSaver) -> None:
        """
        Test for the procedure of reading data from a specific file format.

        :return: None
        """

        pass


    def _writing_process(self, _saver: _BaseSaver, _data: List[list]) -> None:
        """
        Run the truly implementation of running procedure of saving file process. It would also check the running result
        to check it whether be correct or not finally.

        :param _saver: The instance of function *saver* return value in current class.
        :param _data: The data it saves.
        :return: None
        """

        try:
            _saver.open()
            _saver.write(data=_data)
            _saver.close()
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert True, "It work finely!"

        self._writing_procedure_expected_result(_saver=_saver)


    def _writing_procedure_expected_result(self, _saver: _BaseSaver) -> None:
        """
        Check the final running result whether is correct or not at writing process.

        :param _saver: The instance of function *file_format* return value in current class.
        :return: None
        """

        # # # # Test for writing  procedure
        assert Open_Process is True, "It should run *open* process."
        assert Write_Process is True, "It should run *write* process."
        assert Read_Process is False, "It should NOT run *read* process."
        assert Close_Process is True, "It should run *close* process."

        assert Saver_Process is not None and len(Saver_Process) == 3, "The list of recording processes should not be empty and its length is 3."
        assert Saver_Process[0] == "open" and Saver_Process[1] == "write" and Saver_Process[2] == "close", "The content of recording list should be 'open', 'write' and 'close'."

        # # # # Test for saver attribute if it be used with writing
        assert _saver.file_path == _File_Name, "The property of *file_path* should be same as '_File_Name'."
        assert _saver.mode == _Mode, "The property of *mode* should be same as '_Mode'."
        assert _saver.encoding == _Encoding, "The property of *encoding* should be same as '_Encoding'."

        # # # # Test for writing data
        self._check_data_rows(_data=Writing_Data)


    def _reading_process(self, _saver: _BaseSaver) -> None:
        """
        Run the truly implementation of reading file process. It would also check the running result
        to check it whether be correct or not finally.

        :param _saver: The instance of function *file_format* return value in current class.
        :return: None
        """

        try:
            _saver.open()
            _data = _saver.read()
            _saver.close()
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert True, "It work finely!"

        self._reading_procedure_expected_result(_saver=_saver, _data=_data)


    def _reading_procedure_expected_result(self, _saver: _BaseSaver, _data: List[list]) -> None:
        """
        Check the final running result whether is correct or not at reading process.

        :param _saver: The instance of function *file_format* return value in current class.
        :param _data: The data which it gets via reading the file.
        :return: None
        """

        # # # # Test for reading  procedure
        assert Open_Process is True, "It should run *open* process."
        assert Write_Process is False, "It should NOT run *write* process."
        assert Read_Process is True, "It should run *read* process."
        assert Close_Process is True, "It should run *close* process."

        assert Saver_Process is not None and len(Saver_Process) == 3, "The list of recording processes should not be empty and its length is 3."
        assert Saver_Process[0] == "open" and Saver_Process[1] == "read" and Saver_Process[2] == "close", "The content of recording list should be 'open', 'read' and 'close'."

        # # # # Test for saver attribute if it be used with reading
        assert _saver.file_path == _File_Name, "The property of *file_path* should be same as '_File_Name'."
        assert _saver.mode == _Mode, "The property of *mode* should be same as '_Mode'."
        assert _saver.encoding == _Encoding, "The property of *encoding* should be same as '_Encoding'."

        # # # # Test for reading data
        self._check_data_rows(_data=_data)


    def _check_data_rows(self, _data: Iterable[Iterable]) -> None:
        """
        Check every data rows of the option *_data* are the same with Test_Data_List.

        :param _data: Target data to check.
        :return: None
        """

        for _data_row, _expected_data_row in zip(_data, Test_Data_List):
            assert type(_data_row) is list, "The type of element in data should be list."
            for _data, _expected_data in zip(_data_row, _expected_data_row):
                assert str(_data) == str(_expected_data), "The value of each data row should be the same."



class TestFileSaver(SaverTestSpec):

    @pytest.fixture(scope="class")
    def saver(self) -> Generic[_BaseSaver]:
        return FileSaver(file=_SpyFileFormat(), file_name=_File_Name, mode=_Mode, encoding=_Encoding)


    def test_writing_procedure(self, saver: _BaseSaver) -> None:
        reset_flag()
        self._writing_process(_saver=saver, _data=Test_Data_List)


    def test_reading_procedure(self, saver: _BaseSaver) -> None:
        reset_flag()
        self._reading_process(_saver=saver)

