from smoothcrawler_appintegration.role.source import CrawlerSource
from smoothcrawler_appintegration.role.processor import CrawlerProcessor
from smoothcrawler_appintegration.task.filebased import FileBasedTask

from ....unit_test._utils.file.format import FormatTestSpec
from .._spec import BaseTestSpecConfig, BaseRoleAndTaskTestSpec

from typing import Iterable, Any, TypeVar, Generic, Union
from abc import abstractmethod
import traceback
import pytest
import os


_FileBasedTask = TypeVar("_FileBasedTask", bound=FileBasedTask)


class FileBasedTestSpecConfig(BaseTestSpecConfig):

    @abstractmethod
    def file_path(self) -> str:
        """
        File path.

        :return: A string type value.
        """

        pass


    @abstractmethod
    def data(self) -> Union[Iterable[Iterable], Any]:
        """
        The Data for testing.

        :return: in generally, it's an iterable type object.
        """

        pass



class SourceWithFileBasedTestSpec(BaseRoleAndTaskTestSpec):

    @property
    @abstractmethod
    def spec_config(self) -> FileBasedTestSpecConfig:
        pass


    @property
    def file_path(self) -> str:
        return self.spec_config.file_path()


    @property
    def data(self) -> Union[Iterable[Iterable], Any]:
        return self.spec_config.data()


    @pytest.fixture(scope="class")
    def role(self, task: Generic[_FileBasedTask]) -> Generic[_FileBasedTask]:
        return CrawlerSource(task=task)


    def test_run_process(self, role: CrawlerSource) -> None:
        try:
            _data = self.data
            role.run_process(data=_data)
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert True, "It work finely!"

        self._chk_running_result()
        self._chk_final_process()


    def _chk_running_result(self, **kwargs) -> None:
        _file_path = self.file_path
        assert _file_path is not None, "The file path should NOT be None value."
        _exist_file = os.path.exists(_file_path)
        assert _exist_file is True, "It should exist a file."


    def _chk_final_process(self) -> None:
        pass



class ProcessorWithFileBasedTestSpec(BaseRoleAndTaskTestSpec):

    @property
    @abstractmethod
    def spec_config(self) -> FileBasedTestSpecConfig:
        pass


    @property
    def file_path(self) -> str:
        return self.spec_config.file_path()


    @property
    def data(self) -> Union[Iterable[Iterable], Any]:
        return self.spec_config.data()


    @pytest.fixture(scope="class")
    def role(self, task: Generic[_FileBasedTask]) -> CrawlerProcessor:
        return CrawlerProcessor(task=task)


    def test_run_process(self, role: CrawlerProcessor) -> None:
        try:
            _data = role.run_process()
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert True, "It work finely!"

        self._chk_running_result(data=_data)
        self._chk_final_process()


    @abstractmethod
    def _chk_running_result(self, **kwargs) -> None:
        pass


    def _chk_final_process(self) -> None:
        _file_path = self.file_path
        FormatTestSpec._remove_files(file=_file_path)


