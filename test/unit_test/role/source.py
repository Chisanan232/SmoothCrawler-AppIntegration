from smoothcrawler_appintegration.role.source import CrawlerSource, CrawlerProducer

from .._dummy_objs import (
    # For recording testing state
    _get_task_processes_list, TaskProcess,
    # For some dummy objects for running test
    DummySourceTask, DummyMsgQueueConfig
)
from ._spec import SourceRoleTestSpec, ProducerTestSpec

import pytest



class TestCrawlerSource(SourceRoleTestSpec):

    @pytest.fixture(scope="class")
    def role(self, task: DummySourceTask) -> CrawlerSource:
        return CrawlerSource(task=task)


    def _chk_running_result(self) -> None:
        _task_processes_list = _get_task_processes_list()

        assert len(_task_processes_list) == self._procedure_steps_number, f"In file based case, the steps number in procedure should be {self._procedure_steps_number} (initial(open) -> write -> close)."
        assert _task_processes_list[0] == TaskProcess.Init, "The first step should be initialization like open file IO stream."
        assert _task_processes_list[1] == TaskProcess.Generate, "The second step should be write target data into file."
        assert _task_processes_list[2] == TaskProcess.Close, "The latest step (the third one) should be close the file IO stream."



class TestCrawlerProducer(ProducerTestSpec):

    def config(self) -> DummyMsgQueueConfig:
        return DummyMsgQueueConfig()


    @pytest.fixture(scope="class")
    def role(self, task: DummySourceTask) -> CrawlerProducer:
        return CrawlerProducer(task=task)


    def _chk_running_result(self) -> None:
        _task_processes_list = _get_task_processes_list()

        assert len(_task_processes_list) == self._procedure_steps_number * self._procedure_steps_running_times, f"In message queue case, the steps number in procedure should be {self._procedure_steps_number} (initial(build connection) -> send -> close)."

        for _i in range(self._procedure_steps_number):
            _init_index = 0 + (self._procedure_steps_number * _i)
            _send_index = 1 + (self._procedure_steps_number * _i)
            _close_index = 2 + (self._procedure_steps_number * _i)

            assert _task_processes_list[_init_index] == TaskProcess.Init, "The first step should be initialization like building TCP connection with the message queue middle system."
            assert _task_processes_list[_send_index] == TaskProcess.Generate, "The second step should be sending data to message queue middle system."
            assert _task_processes_list[_close_index] == TaskProcess.Close, "The latest step (the third one) should be close the TCP connection with message queue middle system."

