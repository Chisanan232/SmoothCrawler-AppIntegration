from typing import Iterable, Callable, Any, Optional, TypeVar, Generic, cast
from abc import ABCMeta, ABC, abstractmethod

from ..task.messagequeue import MessageQueueConfig as _MessageQueueConfig, MessageQueueTask as _MessageQueueTask
from ..task.framework import (
    ApplicationIntegrationTask as _ApplicationIntegrationTask,
    ApplicationIntegrationSourceTask as _ApplicationIntegrationSourceTask,
    ApplicationIntegrationProcessorTask as _ApplicationIntegrationProcessorTask
)


_BaseTask = TypeVar("_BaseTask", bound=_ApplicationIntegrationTask)
_SourceTask = TypeVar("_SourceTask", bound=_ApplicationIntegrationSourceTask)
_ProcessorTask = TypeVar("_ProcessorTask", bound=_ApplicationIntegrationProcessorTask)
_MQTask = TypeVar("_MQTask", bound=_MessageQueueTask)


class ApplicationIntegrationRole(metaclass=ABCMeta):

    def __init__(self, task: Generic[_BaseTask]):
        self._task: _BaseTask = task


    @abstractmethod
    def _init(self, *args, **kwargs) -> Any:
        pass


    @abstractmethod
    def run_process(self, **kwargs) -> Optional[Any]:
        pass


    @abstractmethod
    def _close(self) -> None:
        pass



class BaseSource(ApplicationIntegrationRole):

    def __init__(self, task: Generic[_SourceTask]):
        super(BaseSource, self).__init__(task=task)
        self._task = cast(_SourceTask, self._task)


    def run_process(self, **kwargs) -> None:
        self._init()
        _data = kwargs.get("data")
        self._write(data=_data)
        self._close()


    @abstractmethod
    def _write(self, data: Iterable[Iterable]) -> Optional[Any]:
        pass



class BaseProcessor(ApplicationIntegrationRole):

    def __init__(self, task: Generic[_ProcessorTask]):
        super(BaseProcessor, self).__init__(task=task)
        self._task = cast(_ProcessorTask, self._task)


    def run_process(self, **kwargs) -> Optional[Any]:
        self._init()
        _data = self._read()
        self._close()
        return _data


    @abstractmethod
    def _read(self) -> Optional[Any]:
        pass



class MessageQueueRole(ApplicationIntegrationRole, ABC):

    def __init__(self, task: Generic[_MQTask]):
        super(MessageQueueRole, self).__init__(task=task)
        self._task = cast(_MessageQueueTask, self._task)



class BaseProducer(MessageQueueRole):

    def run_process(self, config: _MessageQueueConfig, send_args: dict) -> None:
        self._init(config=config)
        assert type(send_args) is dict, "The type of option *send_args* should be a dict."
        self._send(**send_args)
        self._close()


    @abstractmethod
    def _send(self, **kwargs) -> None:
        pass



class BaseConsumer(MessageQueueRole):

    def run_process(self, config: _MessageQueueConfig, poll_args: dict) -> None:
        self._init(config=config)
        assert type(poll_args) is dict, "The type of option *poll_args* should be a dict."
        self._poll(**poll_args)
        self._close()


    @abstractmethod
    def _poll(self, **kwargs) -> Any:
        pass


    def format_callback(self, callback: Callable) -> Callable:
        return self._task.generate_poll_callable(callback=callback)

