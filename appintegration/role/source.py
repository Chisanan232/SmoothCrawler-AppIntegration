from typing import Iterable, Any

try:
    # It should install this package if user want to run the object *RabbitMQTask*
    # command line: pip install pika
    from pika import BasicProperties
except ImportError:
    pass

from ..task.messagequeue import MessageQueueConfig as _MessageQueueConfig
from .framework import BaseSource, BaseProducer, BaseMessageQueueArgument



class CrawlerSource(BaseSource):

    def _init(self, *args, **kwargs) -> Any:
        self._task.init()


    def _write(self, data: Iterable[Iterable]) -> None:
        self._task.generate(data=data)


    def _close(self) -> None:
        self._task.close()



class ProducerArgument(BaseMessageQueueArgument):

    @staticmethod
    def kafka(topic: str, value: bytes, key: str = bytes(), partition=None, timestamp_ms=None) -> dict:
        return {
            "topic": topic,
            "value": value,
            "key": key,
            "partition": partition,
            "timestamp_ms": timestamp_ms
        }


    @staticmethod
    def rabbitmq(exchange: str, routing_key: str, body: bytes, default_queue: str = "", properties: BasicProperties = None, mandatory: bool = False) -> dict:
        return {
            "exchange": exchange,
            "routing_key": routing_key,
            "body": body,
            "default_queue": default_queue,
            "properties": properties,
            "mandatory": mandatory,
        }


    @staticmethod
    def activemq(destination: str, body: str, content_type: str = None, headers: dict = None, **keyword_headers) -> dict:
        return {
            "destination": destination,
            "body": body,
            "content_type": content_type,
            "headers": headers,
            "keyword_headers": keyword_headers,
        }



class CrawlerProducer(BaseProducer):

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

