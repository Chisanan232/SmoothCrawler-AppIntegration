from typing import Any, Optional

from ..task.messagequeue import MessageQueueConfig as _MessageQueueConfig
from .framework import BaseProcessor as _BaseProcessor, BaseConsumer as _BaseConsumer


class CrawlerProcessor(_BaseProcessor):

    def _init(self, *args, **kwargs) -> Any:
        self._task.init(*args, **kwargs)


    def _read(self) -> Optional[Any]:
        _data = self._task.acquire()
        return _data


    def _close(self) -> None:
        self._task.close()



class CrawlerConsumer(_BaseConsumer):

    def _init(self, config: _MessageQueueConfig, **kwargs) -> Any:
        self._task.init(config=config)


    def _poll(self, **kwargs) -> Any:
        # # Kafka arguments
        # callback: Callable

        # # RabbitMQ arguments
        # queue: str, callback: Callable, auto_ack: bool = False, exclusive: bool = False, consumer_tag: Any = None, arguments: Any = None

        # # ActiveMQ destination: str, callback: Callable, id: str = None, ack:str = "auto", headers: dict = None,
        # **keyword_headers

        self._task.acquire(**kwargs)


    def _close(self) -> None:
        self._task.close()

