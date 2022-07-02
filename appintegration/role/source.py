from typing import Iterable, Any

from ..task.messagequeue import MessageQueueConfig as _MessageQueueConfig
from .framework import BaseSource as _BaseSource, BaseProducer as _BaseProducer


class CrawlerSource(_BaseSource):

    def _init(self, *args, **kwargs) -> Any:
        self._task.init()


    def _write(self, data: Iterable[Iterable]) -> None:
        self._task.generate(data=data)


    def _close(self) -> None:
        self._task.close()



class CrawlerProducer(_BaseProducer):

    def _init(self, config: _MessageQueueConfig, **kwargs) -> None:
        self._task.init(config=config)


    def _send(self, **kwargs) -> None:
        # # Kafka arguments
        # topic: str, value: bytes, key: str = bytes(), partition=None, timestamp_ms=None

        # # RabbitMQ arguments
        # exchange: str, routing_key: str, body: bytes, default_queue: str = "", properties: BasicProperties = None, mandatory: bool = False

        # # ActiveMQ
        # destination: str, body: str, content_type: str = None, headers: dict = None, **keyword_headers

        self._task.generate(**kwargs)


    def _close(self) -> None:
        self._task.close()

