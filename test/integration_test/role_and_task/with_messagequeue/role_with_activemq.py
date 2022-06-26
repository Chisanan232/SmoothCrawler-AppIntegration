from appintegration.task.messagequeue import MessageQueueConfig, ActiveMQConfig, ActiveMQTask
from appintegration.arguments import ProducerArgument, ConsumerArgument

from ._spec import (
    # For testing config and its operations
    add_msg_cnt, add_msg_queue, TestingMessageCnt,
    # For SUT (config, role and task)
    MsgQueueTestSpecConfig, RoleWithMessageQueueTaskTestSpec
)

from typing import Iterable, Any, TypeVar, Generic, Union
import pytest


_MsgQueueConfig = TypeVar("_MsgQueueConfig", bound=MessageQueueConfig)


class ActiveMQTestSpecConfig(MsgQueueTestSpecConfig):

    def topic(self) -> str:
        return "/topic/PyTestActive"


    def data(self) -> Union[Iterable[Iterable], Any]:
        return [f"This is testing {i} message." for i in range(TestingMessageCnt)]



class TestRoleWithActiveMQTask(RoleWithMessageQueueTaskTestSpec):

    @property
    def spec_config(self) -> ActiveMQTestSpecConfig:
        return ActiveMQTestSpecConfig()


    @pytest.fixture(scope="class")
    def config(self) -> ActiveMQConfig:
        return ActiveMQConfig([("127.0.0.1", 61613)])


    @pytest.fixture(scope="class")
    def task(self) -> ActiveMQTask:
        return ActiveMQTask()


    def _sending_argument(self, msg: Union[str, bytes]) -> dict:
        _topic = self.topic
        return ProducerArgument.activemq(destination=_topic, body=msg)


    def _receive_argument(self) -> dict:

        def _callback(frame) -> None:
            assert frame is not None, "The message from Kafka should NOT be empty."
            add_msg_queue(msg=frame)
            _msg_cnt = add_msg_cnt()
            if _msg_cnt == TestingMessageCnt - 1:
                raise InterruptedError("Stop the thread for consumer.")

        _topic = self.topic
        return ConsumerArgument.activemq(destination=_topic, callback=_callback)

