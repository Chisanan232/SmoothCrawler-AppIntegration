from typing import Callable, Any
from abc import ABCMeta, abstractmethod

try:
    # It should install this package if user want to run the object *RabbitMQTask*
    # command line: pip install pika
    from pika import BasicProperties
except ImportError:
    pass



class BaseMessageQueueArgument(metaclass=ABCMeta):

    def __init__(self):
        raise Exception("This is a static factory so you shouldn't instantiate this object.")


    @staticmethod
    @abstractmethod
    def kafka(**kwargs):
        pass


    @staticmethod
    @abstractmethod
    def rabbitmq(**kwargs):
        pass


    @staticmethod
    @abstractmethod
    def activemq(**kwargs):
        pass



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



class ConsumerArgument(BaseMessageQueueArgument):

    @staticmethod
    def kafka(callback: Callable) -> dict:
        return {
            "callback": callback
        }


    @staticmethod
    def rabbitmq(queue: str, callback: Callable, auto_ack: bool = False, exclusive: bool = False, consumer_tag: Any = None, arguments: Any = None) -> dict:
        return {
            "queue": queue,
            "callback": callback,
            "auto_ack": auto_ack,
            "exclusive": exclusive,
            "consumer_tag": consumer_tag,
            "arguments": arguments,
        }


    @staticmethod
    def activemq(destination: str, callback: Callable, id: str = None, ack: str = "auto", headers: dict = None, **keyword_headers) -> dict:
        return {
            "destination": destination,
            "callback": callback,
            "id": id,
            "ack": ack,
            "headers": headers,
            "keyword_headers": keyword_headers,
        }
