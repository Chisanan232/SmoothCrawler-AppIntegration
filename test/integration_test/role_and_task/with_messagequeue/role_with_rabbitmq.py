from smoothcrawler_appintegration.task.messagequeue import MessageQueueConfig, RabbitMQConfig, RabbitMQTask
from smoothcrawler_appintegration.arguments import ProducerArgument, ConsumerArgument

from ._spec import (
    # For testing config and its operations
    add_msg_cnt, add_msg_queue, TestingMessageCnt,
    # For SUT (config, role and task)
    MsgQueueTestSpecConfig, RoleWithMessageQueueTaskTestSpec
)

from typing import Iterable, Any, TypeVar, Generic, Union
from pika import PlainCredentials
import pytest


_MsgQueueConfig = TypeVar("_MsgQueueConfig", bound=MessageQueueConfig)


class RabbitMQTestSpecConfig(MsgQueueTestSpecConfig):

    def topic(self) -> str:
        return "test-rabbit"


    def data(self) -> Union[Iterable[Iterable], Any]:
        return [bytes(f"This is testing {i} message.", "utf-8") for i in range(TestingMessageCnt)]



class TestRoleWithRabbitMQTask(RoleWithMessageQueueTaskTestSpec):

    @property
    def spec_config(self) -> RabbitMQTestSpecConfig:
        return RabbitMQTestSpecConfig()


    @pytest.fixture(scope="class")
    def config(self) -> RabbitMQConfig:
        return RabbitMQConfig("localhost", 5672, "/", PlainCredentials("user", "password"))


    @pytest.fixture(scope="class")
    def task(self) -> RabbitMQTask:
        return RabbitMQTask()


    def _sending_argument(self, msg: Union[str, bytes]) -> dict:
        _topic = self.topic
        return ProducerArgument.rabbitmq(exchange="", routing_key=_topic, body=msg, default_queue=_topic)


    def _receive_argument(self) -> dict:

        def _callback(ch, method, properties, body) -> None:
            assert ch is not None, "The message channel from RabbitMQ should NOT be empty."
            assert method is not None, "The message method from RabbitMQ should NOT be empty."
            assert properties is not None, "The message properties from RabbitMQ should NOT be empty."
            assert body is not None, "The message body from RabbitMQ should NOT be empty."

            add_msg_queue(msg=body)
            _msg_cnt = add_msg_cnt()
            # if _msg_cnt == TestingMessageCnt - 1:
            #     raise InterruptedError("Stop the thread for consumer.")

        _topic = self.topic
        return ConsumerArgument.rabbitmq(queue=_topic, callback=_callback, auto_ack=True)

