from appintegration.task.messagequeue import MessageQueueConfig, KafkaConfig, KafkaTask
from appintegration.role.processor import ConsumerArgument
from appintegration.role.source import ProducerArgument

from ._spec import (
    # For testing config and its operations
    add_msg_cnt, add_msg_queue, TestingMessageCnt,
    # For SUT (config, role and task)
    MsgQueueTestSpecConfig, RoleWithMessageQueueTaskTestSpec
)

from typing import Iterable, Any, TypeVar, Generic, Union
import pytest


_MsgQueueConfig = TypeVar("_MsgQueueConfig", bound=MessageQueueConfig)


class KafkaTestSpecConfig(MsgQueueTestSpecConfig):

    def topic(self) -> str:
        return "test-kafka-topic"


    def data(self) -> Union[Iterable[Iterable], Any]:
        return [bytes(f"This is testing {i} message.", "utf-8") for i in range(TestingMessageCnt)]



class TestRoleWithKafkaTask(RoleWithMessageQueueTaskTestSpec):

    @property
    def spec_config(self) -> KafkaTestSpecConfig:
        return KafkaTestSpecConfig()


    @pytest.fixture(scope="class")
    def producer_config(self, config: Generic[_MsgQueueConfig]) -> KafkaConfig:
        return KafkaConfig(role="producer")


    @pytest.fixture(scope="class")
    def consumer_config(self, config: Generic[_MsgQueueConfig]) -> KafkaConfig:
        _topics = self.topic
        return KafkaConfig(role="consumer", topics=_topics)


    @pytest.fixture(scope="class")
    def task(self) -> KafkaTask:
        return KafkaTask()


    def _sending_argument(self, msg: Union[str, bytes]) -> dict:
        _topic = self.topic
        return ProducerArgument.kafka(topic=_topic, value=msg)


    def _receive_argument(self) -> dict:

        def _callback(msg: str) -> None:
            assert msg is not None, "The message from Kafka should NOT be empty."
            add_msg_queue(msg=msg)
            _msg_cnt = add_msg_cnt()
            if _msg_cnt == TestingMessageCnt - 1:
                raise InterruptedError("Stop the thread for consumer.")

        return ConsumerArgument.kafka(callback=_callback)

