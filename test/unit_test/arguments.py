from appintegration.arguments import BaseMessageQueueArgument, ConsumerArgument, ProducerArgument

from abc import ABCMeta, abstractmethod
from typing import Type, TypeVar
import pytest


_BaseMessageQueueArgument = TypeVar("_BaseMessageQueueArgument", bound=BaseMessageQueueArgument)


class MessageQueueArgumentsTestSpec(metaclass=ABCMeta):

    @pytest.fixture(scope="class")
    @abstractmethod
    def argument(self) -> Type[_BaseMessageQueueArgument]:
        pass


    def test_instantiate(self, argument: Type[_BaseMessageQueueArgument]) -> None:
        try:
            argument()
        except Exception as e:
            assert "This is a static factory so you shouldn't instantiate this object." in str(e), \
                "It should raise an exception about this object cannot instantiate because it's static factory."
        else:
            assert False, \
                "It should raise an exception about this object cannot instantiate because it's static factory."


    @abstractmethod
    def test_kafka(self, argument: Type[_BaseMessageQueueArgument]) -> None:
        pass


    @abstractmethod
    def test_rabbit(self, argument: Type[_BaseMessageQueueArgument]) -> None:
        pass


    @abstractmethod
    def test_activemq(self, argument: Type[_BaseMessageQueueArgument]) -> None:
        pass



class TestConsumerArguments(MessageQueueArgumentsTestSpec):

    @pytest.fixture(scope="class")
    def argument(self) -> Type[ConsumerArgument]:
        return ConsumerArgument


    def test_kafka(self, argument: Type[ConsumerArgument]) -> None:
        _kafka_args = argument.kafka(callback=self.callback_function)
        assert type(_kafka_args) is dict, "The return value should be a dict type value."
        assert _kafka_args["callback"] == self.callback_function, "The callback function object should be same as *self.callback_function*."


    def test_rabbit(self, argument: Type[ConsumerArgument]) -> None:
        _rabbitmq_args = argument.rabbitmq(queue=self.topic, callback=self.callback_function)
        assert type(_rabbitmq_args) is dict, "The return value should be a dict type value."
        assert _rabbitmq_args["queue"] == self.topic, f"The queue name should be same as {self.topic}."
        assert _rabbitmq_args["callback"] == self.callback_function, "The callback function object should be same as *self.callback_function*."


    def test_activemq(self, argument: Type[ConsumerArgument]) -> None:
        _activemq_args = argument.activemq(destination=self.topic, callback=self.callback_function)
        assert type(_activemq_args) is dict, "The return value should be a dict type value."
        assert _activemq_args["destination"] == self.topic, f"The queue name should be same as {self.topic}."
        assert _activemq_args["callback"] == self.callback_function, "The callback function object should be same as *self.callback_function*."


    @property
    def topic(self) -> str:
        return "test-topic"


    def callback_function(self, msg) -> None:
        print(msg)



class TestProducerArguments(MessageQueueArgumentsTestSpec):

    @pytest.fixture(scope="class")
    def argument(self) -> Type[ProducerArgument]:
        return ProducerArgument


    def test_kafka(self, argument: Type[ProducerArgument]) -> None:
        _kafka_args = argument.kafka(topic=self.topic, value=self.msg_bytes)
        assert type(_kafka_args) is dict, "The return value should be a dict type value."
        assert _kafka_args["topic"] == self.topic, f"The topic name should be same as {self.topic}."
        assert _kafka_args["value"] == self.msg_bytes, f"The message content should be same as {self.msg_bytes}."


    def test_rabbit(self, argument: Type[ProducerArgument]) -> None:
        _rabbitmq_args = argument.rabbitmq(exchange="", routing_key=self.topic, body=self.msg_bytes)
        assert type(_rabbitmq_args) is dict, "The return value should be a dict type value."
        assert _rabbitmq_args["exchange"] == "", "The exchange should be same as ''."
        assert _rabbitmq_args["routing_key"] == self.topic, f"The routing key should be same as {self.topic}."
        assert _rabbitmq_args["body"] == self.msg_bytes, f"The message content should be same as {self.msg_bytes}."


    def test_activemq(self, argument: Type[ProducerArgument]) -> None:
        _activemq_args = argument.activemq(destination=self.topic, body=self.msg_str)
        assert type(_activemq_args) is dict, "The return value should be a dict type value."
        assert _activemq_args["destination"] == self.topic, f"The topic name should be same as {self.topic}."
        assert _activemq_args["body"] == self.msg_str, f"The message content should be same as {self.msg_str}."


    @property
    def topic(self) -> str:
        return "test-topic"


    @property
    def msg_str(self) -> str:
        return "this is message."


    @property
    def msg_bytes(self) -> bytes:
        return b"this is message."

