from appintegration.task.framework import ApplicationIntegrationSourceTask, ApplicationIntegrationProcessorTask
from appintegration.task.messagequeue import (
    MessageQueueConfig, MessageQueueTask,
    KafkaConfig, KafkaTask
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


def _reset_test_state() -> None:
    global MessageQueueCnt, MessageQueueBodies, Global_Exception
    MessageQueueCnt = 0
    MessageQueueBodies.clear()
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

    """
    Spec of testing items about objects **XXXTask** of module *appintegration.task.messagequeue*.
    In other words, it means that for the sub-class of object **MessageQueueTask**.
    """

    @pytest.fixture(scope="class")
    def config(self) -> Generic[_MQTask]:
        """
        Which object **MessageQueueConfig** it should test for. This is the default of
        functions *config_for_producer* and *config_for_consumer*. So it could only
        override this function, rather than 2 others to let both of them return the same
        instance **MessageQueueConfig**.

        :return: The instance of sub-class of **MessageQueueConfig** and it's the default
                      of other 2 functions *config_for_producer* and *config_for_consumer*.
        """

        pass


    @pytest.fixture(scope="class")
    def config_for_producer(self, config) -> Generic[_MQTask]:
        """
        The object is sub-class of **MessageQueueConfig** to test. This object for
        component *Processor Application* or be called *Producer*.

        :param config: The default value. Please see more detail in function *config*.
        :return: The instance of object for component *Processor Application* or be called *Producer*.
        """

        pass


    @pytest.fixture(scope="class")
    def config_for_consumer(self, config) -> Generic[_MQTask]:
        """
        The object is sub-class of **MessageQueueConfig** to test. This object for
        component *Source Application* or be called *Consumer*.

        :param config: The default value. Please see more detail in function *config*.
        :return: The instance of object for component *Source Application* or be called *Consumer*.
        """

        pass


    @pytest.fixture(scope="class")
    @abstractmethod
    def task_for_generating(self, config_for_producer: Generic[_MsgQueueConfig]) -> Generic[_MQTask]:
        """
        The object for test which is responsible of generating something in source application.
        In *Producer* speaking, it means publish something (in generally, it's a message) to
        message middle component system.

        :param config_for_producer: The instance of sub-class of **MessageQueueConfig** for *Source* (or means *Producer*).
        :return: The instance of sub-class of **MessageQueueTask**.
        """

        pass


    @pytest.fixture(scope="class")
    @abstractmethod
    def task_for_acquiring(self, config_for_consumer: Generic[_MsgQueueConfig]) -> Generic[_MQTask]:
        """
        The object for test which is responsible of acquire something in processor application.
        In *Consumer* speaking, it means subscribe to get something (in generally, it's a message)
        from message middle component system.

        :param config_for_consumer: The instance of sub-class of **MessageQueueConfig** for *Processor* (or means *Consumer*).
        :return: The instance of sub-class of **MessageQueueTask**.
        """

        pass


    def test_publish_and_subscribe_features(self, task_for_generating: Generic[_MQTask], task_for_acquiring: Generic[_MQTask]):
        """
        This is the major function to run testing. It would test producer and consumer in the same time.

        :param task_for_generating: The instance of sub-class of **MessageQueueTask** for *Producer*.
        :param task_for_acquiring: The instance of sub-class of **MessageQueueTask** for *Consumer*.
        :return: None
        """

        _test_consumer = threading.Thread(target=self._subscribing_process, args=(task_for_acquiring, ))
        _test_producer = threading.Thread(target=self._publishing_process, args=(task_for_generating, ))

        _test_consumer.start()
        _test_producer.start()

        _test_producer.join()
        _test_consumer.join()

        global Global_Exception
        if Global_Exception is not None:
            raise Global_Exception


    def _publishing_process(self, _task: Generic[_MQTask]) -> None:
        """
        The truly implementation of producing feature usage.
        The running procedure is:

            Run the producing implementation -> Check the running result -> Run some processes finally

        * Run the implementation: _sending_feature
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
    def _sending_feature(self, _task: Generic[_MQTask], topic: str, value: bytes) -> None:
        """
        The truly implement of sending (or it calls publishing) something to message middle component system.

        :param _task: The instance of sub-class of **MessageQueueTask** for *Producer*.
        :param topic: The target topic where the message would be send to.
        :param value: The message it would be send to system.
        :return: None
        """

        pass


    def _subscribing_process(self, _task: Generic[_MQTask]) -> None:
        """
        The truly implementation of consuming feature usage.
        The running procedure is:

            Run the consuming implementation -> Check the running result -> Run some processes finally

        * Run the implementation: _poll_feature
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
    def _poll_feature(self, _task: Generic[_MQTask]) -> None:
        """
        The truly implement of polling (or it calls consuming) something from message middle component system.

        :param _task: The instance of sub-class of **MessageQueueTask** for *Consumer*.
        :return: None
        """

        pass


    @property
    @abstractmethod
    def _testing_topic(self) -> str:
        """
        Which the topic it would send (or publish) message to.

        :return: A string type value which is topic name.
        """

        pass


    @property
    def _testing_data(self) -> Union[Iterable[Iterable], Any]:
        """
        The data for testing which would be sent (or published) to message middle component system.

        :return: In generally, it would be a iterable object.
        """

        return [bytes(f"This is testing {i} message.", "utf-8") for i in range(TestingMessageCnt)]


    @abstractmethod
    def _chk_generate_running_result(self, **kwargs) -> None:
        """
        The checking of the producing running result.

        :param kwargs: Some arguments if it needs.
        :return: None
        """

        pass


    @abstractmethod
    def _chk_acquire_running_result(self, **kwargs) -> None:
        """
        The checking of the consuming running result.

        :param kwargs: Some arguments if it needs.
        :return: None
        """

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

