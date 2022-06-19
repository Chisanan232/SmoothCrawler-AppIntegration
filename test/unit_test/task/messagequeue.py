from appintegration.task.framework import ApplicationIntegrationSourceTask, ApplicationIntegrationProcessorTask
from appintegration.task.messagequeue import (
    MessageQueueConfig, MessageQueueTask,
    KafkaConfig, KafkaTask,
)

from typing import Any, Union, TypeVar, Generic, Iterable
from abc import ABCMeta, abstractmethod
import threading
import pytest
import time


_AppIntegrationTask = Union[ApplicationIntegrationSourceTask, ApplicationIntegrationProcessorTask]

_MsgQueueConfig = TypeVar("_MsgQueueConfig", bound=MessageQueueConfig)
_MQTask = TypeVar("_MQTask", bound=MessageQueueTask)

TestingMessageCnt = 10
MessageQueueCnt: int = 0
MessageQueueBodies: list = []

Global_Exception = None


class MessageQueueConfigTestSpec(metaclass=ABCMeta):

    """
    Spec of testing items about object **XXXConfig** of module *appintegration.task.messagequeue*.
    In other words, it means that for the sub-class of object **MessageQueueConfig**.
    """

    @abstractmethod
    def config(self, **kwargs) -> Generic[_MsgQueueConfig]:
        """
        Which object it should test for.

        :param kwargs: The arguments of the object it may have.
        :return: The instance of the sub-class of **MessageQueueConfig**.
        """

        pass


    @abstractmethod
    def test_generate(self, config: Generic[_MsgQueueConfig]) -> None:
        """
        Test for the function *generate*.

        :param config: The instance of function *config* return value in current class.
        :return: None
        """

        pass



class MessageQueueTaskTestSpec:

    @pytest.fixture(scope="class")
    def config(self) -> Generic[_MQTask]:
        pass


    @pytest.fixture(scope="class")
    def config_for_producer(self, config) -> Generic[_MQTask]:
        pass


    @pytest.fixture(scope="class")
    def config_for_consumer(self, config) -> Generic[_MQTask]:
        pass


    @pytest.fixture(scope="class")
    @abstractmethod
    def task_for_generating(self, config_for_producer: Generic[_MsgQueueConfig]) -> Generic[_MQTask]:
        pass


    @pytest.fixture(scope="class")
    @abstractmethod
    def task_for_acquiring(self, config_for_consumer: Generic[_MsgQueueConfig]) -> Generic[_MQTask]:
        pass


    def test_publish_and_subscribe_features(self, task_for_generating: KafkaTask, task_for_acquiring: KafkaTask):
        _test_consumer = threading.Thread(target=self._subscribing_process, args=(task_for_acquiring, ))
        _test_producer = threading.Thread(target=self._publishing_process, args=(task_for_generating, ))

        _test_consumer.start()
        _test_producer.start()

        _test_producer.join()
        _test_consumer.join()

        global Global_Exception
        if Global_Exception is not None:
            raise Global_Exception


    def _publishing_process(self, _task: KafkaTask) -> None:
        """
        The truly implementation of generating feature usage.
        The running procedure is:

            Run the implementation -> Check the running result -> Run some processes finally

        * Run the implementation: test_generate
        * Check the running result: _chk_generate_running_result
        * Run some processes finally: _chk_generate_final_ps

        :param _task: The instance of *ApplicationIntegrationSourceTask*.
        :return: None
        """

        try:
            # Get data
            _topic = self._testing_topic
            _data = self._testing_data

            for _data_row in _data:
                self._sending_feature(_task=_task, topic=_topic, value=_data_row)
                time.sleep(0.5)

            _task.close()

            self._chk_generate_running_result()
        except Exception as e:
            global Global_Exception
            Global_Exception = e


    @abstractmethod
    def _sending_feature(self, _task: KafkaTask, topic: str, value: bytes) -> None:
        pass


    def _subscribing_process(self, _task: KafkaTask) -> None:
        """
        The truly implementation of acquiring feature usage.
        The running procedure is:

            Run the implementation -> Check the running result -> Run some processes finally

        * Run the implementation: test_acquire
        * Check the running result: _chk_acquire_running_result
        * Run some processes finally: _chk_acquire_final_ps

        :param _task: The instance of *ApplicationIntegrationProcessorTask*.
        :return: None
        """

        try:
            self._poll_feature(_task=_task)
            _task.close()

            self._chk_acquire_running_result()
        except Exception as e:
            global Global_Exception
            Global_Exception = e


    @abstractmethod
    def _poll_feature(self, _task: KafkaTask) -> None:
        pass


    @property
    @abstractmethod
    def _testing_topic(self) -> str:
        pass


    @property
    def _testing_data(self) -> Union[Iterable[Iterable], Any]:
        return [bytes(f"This is testing {i} message.", "utf-8") for i in range(TestingMessageCnt)]


    @abstractmethod
    def _chk_generate_running_result(self, **kwargs) -> None:
        pass


    @abstractmethod
    def _chk_acquire_running_result(self, **kwargs) -> None:
        pass



class TestKafkaConfig(MessageQueueConfigTestSpec):

    def config(self, role: str) -> KafkaConfig:
        return KafkaConfig(role=role)


    @pytest.mark.parametrize("role", ["producer", "consumer"])
    def test_generate(self, role: str) -> None:
        _kafka_config = self.config(role=role).generate()
        assert type(_kafka_config) is dict, "The data type of configuration of MessageQueueConfig should be dict."


    def test_is_producer(self) -> None:
        _config = KafkaConfig(role="producer")
        assert _config.is_producer() is True, "It should be True because we initial *KafkaConfig* as *producer*."
        assert _config.is_consumer() is False, "It should be False because we initial *KafkaConfig* as *producer*."


    def test_is_consumer(self) -> None:
        _config = KafkaConfig(role="consumer")
        assert _config.is_consumer() is True, "It should be True because we initial *KafkaConfig* as *consumer*."
        assert _config.is_producer() is False, "It should be False because we initial *KafkaConfig* as *consumer*."



class TestKafkaTask(MessageQueueTaskTestSpec):

    @pytest.fixture(scope="class")
    def config_for_producer(self) -> KafkaConfig:
        return KafkaConfig(role="producer")


    @pytest.fixture(scope="class")
    def config_for_consumer(self) -> KafkaConfig:
        return KafkaConfig(role="consumer")


    @pytest.fixture(scope="class")
    def task_for_generating(self, config_for_producer: KafkaConfig) -> KafkaTask:
        _kafka_task = KafkaTask()
        _kafka_task.init(config=config_for_producer)
        return _kafka_task


    @pytest.fixture(scope="class")
    def task_for_acquiring(self, config_for_consumer: KafkaConfig) -> KafkaTask:
        _kafka_task = KafkaTask()
        _kafka_task.init(config=config_for_consumer, topics=self._testing_topic)
        return _kafka_task


    def _sending_feature(self, _task: KafkaTask, topic: str, value: bytes) -> None:
        # _task.send(topic=topic, value=value)
        _task.generate(topic=topic, value=value)


    def _poll_feature(self, _task: KafkaTask) -> None:

        def _callback(msg: str) -> None:
            global MessageQueueBodies, MessageQueueCnt
            assert msg is not None, "The message from Kafka should NOT be empty."
            MessageQueueBodies.append(msg)
            MessageQueueCnt += 1
            if MessageQueueCnt == TestingMessageCnt - 1:
                raise InterruptedError("Stop the thread for consumer.")

        try:
            # _task.poll(callback=_callback)
            _task.acquire(callback=_callback)
        except Exception as e:
            assert type(e) is InterruptedError, ""


    @property
    def _testing_topic(self) -> str:
        return "pytest-kafka"


    def _chk_generate_running_result(self, **kwargs) -> None:
        pass


    def _chk_acquire_running_result(self, **kwargs) -> None:
        global MessageQueueBodies, MessageQueueCnt

        assert len(MessageQueueBodies) == TestingMessageCnt - 1, ""
        assert MessageQueueCnt == TestingMessageCnt - 1, ""

