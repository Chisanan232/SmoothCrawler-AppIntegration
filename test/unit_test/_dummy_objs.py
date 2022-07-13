from smoothcrawler_appintegration.task.messagequeue import MessageQueueConfig
from smoothcrawler_appintegration.task.framework import ApplicationIntegrationSourceTask, ApplicationIntegrationProcessorTask
from smoothcrawler_appintegration.role.framework import BaseSource, BaseProducer, BaseProcessor, BaseConsumer
from smoothcrawler_appintegration.url import API, ApplicationIntegrationURL

from typing import List, Iterable, TypeVar, Any, Optional, Union
from enum import Enum


_API = TypeVar("_API", bound=API)
_ApplicationIntegrationURL = TypeVar("_ApplicationIntegrationURL", bound=ApplicationIntegrationURL)


class RoleProcess(Enum):

    Init = "init"
    Write = "_write"
    Read = "_read"
    Send = "_send"
    Poll = "_poll"
    Close = "close"


class TaskProcess(Enum):

    Init = "init"
    Generate = "generate"
    Acquire = "acquire"
    Close = "close"


_Role_Processes_List: List[RoleProcess] = []
_Task_Processes_List: List[TaskProcess] = []


def _get_role_processes_list() -> list:
    return _Role_Processes_List


def _get_task_processes_list() -> list:
    return _Task_Processes_List


def _reset_processes_list() -> None:
    global _Role_Processes_List, _Task_Processes_List
    _Role_Processes_List.clear()
    _Task_Processes_List.clear()


class DummySourceTask(ApplicationIntegrationSourceTask):

    def init(self, *args, **kwargs) -> Any:
        global _Task_Processes_List
        _Task_Processes_List.append(TaskProcess.Init)

    def generate(self, **kwargs) -> Optional[Any]:
        global _Task_Processes_List
        _Task_Processes_List.append(TaskProcess.Generate)

    def close(self) -> None:
        global _Task_Processes_List
        _Task_Processes_List.append(TaskProcess.Close)


class DummyProcessorTask(ApplicationIntegrationProcessorTask):

    def init(self, *args, **kwargs) -> Any:
        global _Task_Processes_List
        _Task_Processes_List.append(TaskProcess.Init)

    def acquire(self) -> Optional[Any]:
        global _Task_Processes_List
        _Task_Processes_List.append(TaskProcess.Acquire)

    def close(self) -> None:
        global _Task_Processes_List
        _Task_Processes_List.append(TaskProcess.Close)



class DummySource(BaseSource):

    def __init__(self, task: DummySourceTask):
        super().__init__(task)

    def _init(self, *args, **kwargs) -> Any:
        global _Role_Processes_List
        _Role_Processes_List.append(RoleProcess.Init)
        self._task.init()

    def _write(self, data: Iterable[Iterable]) -> Optional[Any]:
        global _Role_Processes_List
        _Role_Processes_List.append(RoleProcess.Write)
        self._task.generate(data=None)

    def _close(self) -> None:
        global _Role_Processes_List
        _Role_Processes_List.append(RoleProcess.Close)
        self._task.close()



class DummyProducer(BaseProducer):

    def __init__(self, task: DummySourceTask):
        super().__init__(task)

    def _init(self, config) -> Any:
        global _Role_Processes_List
        _Role_Processes_List.append(RoleProcess.Init)
        self._task.init()

    def _send(self, **kwargs) -> None:
        global _Role_Processes_List
        _Role_Processes_List.append(RoleProcess.Send)
        self._task.generate(**kwargs)

    def _close(self) -> None:
        global _Role_Processes_List
        _Role_Processes_List.append(RoleProcess.Close)
        self._task.close()



class DummyProcessor(BaseProcessor):

    def __init__(self, task: DummySourceTask):
        super().__init__(task)

    def _init(self, *args, **kwargs) -> Any:
        global _Role_Processes_List
        _Role_Processes_List.append(RoleProcess.Init)
        self._task.init()

    def _read(self) -> Optional[Any]:
        global _Role_Processes_List
        _Role_Processes_List.append(RoleProcess.Read)
        self._task.generate(data=None)

    def _close(self) -> None:
        global _Role_Processes_List
        _Role_Processes_List.append(RoleProcess.Close)
        self._task.close()



class DummyConsumer(BaseConsumer):

    def __init__(self, task: DummySourceTask):
        super().__init__(task)

    def _init(self, config) -> Any:
        global _Role_Processes_List
        _Role_Processes_List.append(RoleProcess.Init)
        self._task.init()

    def _poll(self, **kwargs) -> Any:
        global _Role_Processes_List
        _Role_Processes_List.append(RoleProcess.Poll)
        self._task.generate(**kwargs)

    def _close(self) -> None:
        global _Role_Processes_List
        _Role_Processes_List.append(RoleProcess.Close)
        self._task.close()



class DummyMsgQueueConfig(MessageQueueConfig):

    def generate(self, **kwargs) -> Union[dict, Any]:
        return {}

    @classmethod
    def send_arguments(cls, **kwargs) -> dict:
        return {"value": b""}

    @classmethod
    def poll_arguments(cls, **kwargs) -> dict:
        return {}


_Dummy_Arguments: dict = {"value": b""}

