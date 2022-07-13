from smoothcrawler_appintegration.role.processor import CrawlerProcessor, CrawlerConsumer

from .._dummy_objs import (
    # For recording testing state
    _get_task_processes_list, TaskProcess,
    # For some dummy objects for running test
    DummyProcessorTask, DummyMsgQueueConfig
)
from ._spec import ProcessorRoleTestSpec, ConsumerTestSpec

import pytest



class TestCrawlerSource(ProcessorRoleTestSpec):

    @pytest.fixture(scope="class")
    def role(self, task: DummyProcessorTask) -> CrawlerProcessor:
        return CrawlerProcessor(task=task)


    def _chk_running_result(self, data) -> None:
        _task_processes_list = _get_task_processes_list()

        assert len(_task_processes_list) == self._procedure_steps_number, f"In file based case, the steps number in procedure should be {self._procedure_steps_number} (initial(open) -> write -> close)."
        assert _task_processes_list[0] == TaskProcess.Init, "The first step should be initialization like open file IO stream."
        assert _task_processes_list[1] == TaskProcess.Acquire, "The second step should be write target data into file."
        assert _task_processes_list[2] == TaskProcess.Close, "The latest step (the third one) should be close the file IO stream."



class TestCrawlerProducer(ConsumerTestSpec):

    def config(self) -> DummyMsgQueueConfig:
        return DummyMsgQueueConfig()


    @pytest.fixture(scope="class")
    def role(self, task: DummyProcessorTask) -> CrawlerConsumer:
        return CrawlerConsumer(task=task)


    def _chk_running_result(self) -> None:
        _task_processes_list = _get_task_processes_list()

        assert len(_task_processes_list) == self._procedure_steps_number, f"In message queue case, the steps number in procedure should be {self._procedure_steps_number} (initial(build connection) -> send -> close)."

        assert _task_processes_list[0] == TaskProcess.Init, "The first step should be initialization like building TCP connection with the message queue middle system."
        assert _task_processes_list[1] == TaskProcess.Acquire, "The second step should be sending data to message queue middle system."
        assert _task_processes_list[2] == TaskProcess.Close, "The latest step (the third one) should be close the TCP connection with message queue middle system."

