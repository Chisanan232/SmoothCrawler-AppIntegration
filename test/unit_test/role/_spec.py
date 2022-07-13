from smoothcrawler_appintegration.task.messagequeue import MessageQueueConfig
from smoothcrawler_appintegration.role.framework import ApplicationIntegrationRole, MessageQueueRole

from ..._data import Test_Data_List
from .._dummy_objs import (
    # For recording testing state
    _reset_processes_list,
    # For some dummy objects for running test
    DummySourceTask, DummyProcessorTask, _Dummy_Arguments
)

from typing import TypeVar, Generic
from abc import ABCMeta, ABC, abstractmethod
import pytest


_AppIntegrationRole = TypeVar("_AppIntegrationRole", bound=ApplicationIntegrationRole)
_MsgQueueRole = TypeVar("_MsgQueueRole", bound=MessageQueueRole)
_MsgQueueConfig = TypeVar("_MsgQueueConfig", bound=MessageQueueConfig)


class RoleTestSpec(metaclass=ABCMeta):

    @pytest.fixture(scope="class")
    @abstractmethod
    def role(self, task: DummySourceTask) -> Generic[_AppIntegrationRole]:
        pass


    @property
    def _procedure_steps_number(self) -> int:
        return 3


    @abstractmethod
    def test_run_process(self, role: Generic[_AppIntegrationRole]) -> None:
        pass


    @abstractmethod
    def _chk_running_result(self, **kwargs) -> None:
        pass



class SourceRoleTestSpec(RoleTestSpec, ABC):

    @pytest.fixture(scope="class")
    def task(self) -> DummySourceTask:
        return DummySourceTask()


    def test_run_process(self, role: Generic[_AppIntegrationRole]) -> None:
        _reset_processes_list()

        role.run_process(data=Test_Data_List)
        self._chk_running_result()


    @abstractmethod
    def _chk_running_result(self) -> None:
        pass



class ProcessorRoleTestSpec(RoleTestSpec, ABC):

    @pytest.fixture(scope="class")
    def task(self) -> DummyProcessorTask:
        return DummyProcessorTask()


    def test_run_process(self, role: Generic[_AppIntegrationRole]) -> None:
        _reset_processes_list()

        _data = role.run_process()
        self._chk_running_result(data=_data)


    @abstractmethod
    def _chk_running_result(self, data) -> None:
        pass



class MsgQueueRoleTestSpec(RoleTestSpec):

    @abstractmethod
    def config(self) -> Generic[_MsgQueueConfig]:
        pass


    @pytest.fixture(scope="class")
    @abstractmethod
    def role(self) -> Generic[_MsgQueueRole]:
        pass


    @property
    def _procedure_steps_running_times(self) -> int:
        return 3



class ProducerTestSpec(MsgQueueRoleTestSpec, ABC):

    @pytest.fixture(scope="class")
    def task(self) -> DummySourceTask:
        return DummySourceTask()


    def test_run_process(self, role: _MsgQueueRole) -> None:
        _reset_processes_list()

        _config = self.config()
        for _ in Test_Data_List:
            role.run_process(config=_config, send_args=_Dummy_Arguments)
        self._chk_running_result()



class ConsumerTestSpec(MsgQueueRoleTestSpec, ABC):

    @pytest.fixture(scope="class")
    def task(self) -> DummyProcessorTask:
        return DummyProcessorTask()


    def test_run_process(self, role: _MsgQueueRole) -> None:
        _reset_processes_list()

        _config = self.config()
        role.run_process(config=_config, poll_args={})
        self._chk_running_result()

