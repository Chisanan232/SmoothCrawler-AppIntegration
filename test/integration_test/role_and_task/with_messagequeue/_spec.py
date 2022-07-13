from smoothcrawler_appintegration.role.processor import CrawlerConsumer
from smoothcrawler_appintegration.role.source import CrawlerProducer
from smoothcrawler_appintegration.task.messagequeue import MessageQueueConfig, MessageQueueTask

from .._spec import BaseTestSpecConfig, BaseRoleAndTaskTestSpec

from abc import abstractmethod
from typing import Iterable, Any, TypeVar, Generic, Union
import threading
import pytest
import time


_CrawlerConsumer = TypeVar("_CrawlerConsumer", bound=CrawlerConsumer)
_CrawlerProducer = TypeVar("_CrawlerProducer", bound=CrawlerProducer)

_MsgQueueTask = TypeVar("_MsgQueueTask", bound=MessageQueueTask)
_MsgQueueConfig = TypeVar("_MsgQueueConfig", bound=MessageQueueConfig)

TestingMessageCnt = 10
MessageQueueCnt: int = 0
MessageQueueBodies: list = []

_Global_Testing_Exception = None


def add_msg_cnt() -> int:
    """
    Add 1 of counter when it gets one message every times.

    :return: An integer type value which is current counter.
    """

    global MessageQueueCnt
    MessageQueueCnt += 1
    return MessageQueueCnt


def add_msg_queue(msg: Union[str, bytes]) -> None:
    """
    Add message object it gets into list.

    :param msg: A message object.
    :return: None
    """

    global MessageQueueBodies
    MessageQueueBodies.append(msg)


def _reset_testing_state() -> None:
    """
    Reset all the testing states.

    :return: None
    """

    global MessageQueueCnt, MessageQueueBodies
    MessageQueueCnt = 0
    MessageQueueBodies.clear()


def _reset_exception() -> None:
    """
    Reset the variable saves exception to be None.

    :return: None
    """

    global _Global_Testing_Exception
    _Global_Testing_Exception = None


class MsgQueueTestSpecConfig(BaseTestSpecConfig):

    @abstractmethod
    def topic(self) -> str:
        """
        The topic or queue name of message middle component system.

        :return: A string type value.
        """

        pass


    @abstractmethod
    def data(self) -> Union[Iterable[Iterable], Any]:
        """
        The data for testing which will be sent to message middle component system.

        :return: In generally, it's an iterable object and its elements are string or bytes type.
        """

        pass



class RoleWithMessageQueueTaskTestSpec(BaseRoleAndTaskTestSpec):

    @property
    @abstractmethod
    def spec_config(self) -> MsgQueueTestSpecConfig:
        pass


    @property
    def topic(self) -> str:
        """
        The topic or queue name would be used in testing.

        :return: A topic or queue name as string type value.
        """

        return self.spec_config.topic()


    @property
    def data(self) -> str:
        """
        The data for Producer or Consumer to test.

        :return: An iterable type object.
        """

        return self.spec_config.data()


    @pytest.fixture(scope="class")
    def config(self) -> Generic[_MsgQueueConfig]:
        """
        The default value of *config*. Sometimes, no matter it is *producer* or *consumer*,
        it could use the same arguments to initial *task*. For that case, it could only override
        this function rather than 2 others *producer_config* or *consumer_config*. However,
        if it has different arguments for different objects like **KafkaProducer** and **KafkaConsumer**,
        you could override functions *producer_config* or *consumer_config* to let each of them
        use their own settings.

        :return: The default configuration object.
        """

        pass


    @pytest.fixture(scope="class")
    def producer_config(self, config: Generic[_MsgQueueConfig]) -> Generic[_MsgQueueConfig]:
        """
        Instantiate *MessageQueueConfig* object for *producer* to initial *MessageQueueTask*.

        :param config: he default value of *config*.
        :return: The sub-class of *MessageQueueConfig* instance.
        """

        return config


    @pytest.fixture(scope="class")
    def consumer_config(self, config: Generic[_MsgQueueConfig]) -> Generic[_MsgQueueConfig]:
        """
        Instantiate *MessageQueueConfig* object for *consumer* to initial *MessageQueueTask*.

        :param config: he default value of *config*.
        :return: The sub-class of *MessageQueueConfig* instance.
        """

        return config


    @pytest.fixture(scope="class")
    def producer_task(self, task: Generic[_MsgQueueTask]) -> Generic[_MsgQueueTask]:
        """
        Instantiate *MessageQueueTask* object for *producer*.

        :param task: The default value of *task*.
        :return: The sub-class of *MessageQueueTask* instance.
        """

        return task


    @pytest.fixture(scope="class")
    def consumer_task(self, task: Generic[_MsgQueueTask]) -> Generic[_MsgQueueTask]:
        """
        Instantiate *MessageQueueTask* object for *consumer*.

        :param task: The default value of *task*.
        :return: The sub-class of *MessageQueueTask* instance.
        """

        return task


    @pytest.fixture(scope="class")
    def producer(self, producer_task: Generic[_MsgQueueTask]) -> CrawlerProducer:
        """
        Instantiate *producer* object for testing.

        :param producer_task: The instance of *MessageQueueTask*.
        :return: The instance of *producer* --- **CrawlerProducer**.
        """

        return CrawlerProducer(task=producer_task)


    @pytest.fixture(scope="class")
    def consumer(self, consumer_task: Generic[_MsgQueueTask]) -> CrawlerConsumer:
        """
        Instantiate *consumer* object for testing.

        :param consumer_task: The instance of *MessageQueueTask*.
        :return: The instance of *consumer* --- **CrawlerConsumer**.
        """

        return CrawlerConsumer(task=consumer_task)


    def test_producer_and_consumer(self,
                                   producer: Generic[_CrawlerProducer], producer_config: Generic[_MsgQueueConfig],
                                   consumer: Generic[_CrawlerConsumer], consumer_config: Generic[_MsgQueueConfig]) -> None:
        """
        The major function to run testing. It would activate and run 2 threads to test
        *producer* with *task* and *consumer* with *task*. It test the features here
        simultaneously because it's an **integration test**, so it not only test the
        running of *role* with *task*, but also test entire running different *role*
        to to their own responsibility with each others.

        :param producer: The *Producer* instance.
        :param producer_config: The configuration instance for *Producer*.
        :param consumer: The *Consumer* instance.
        :param consumer_config: The configuration instance for *Consumer*.
        :return: None
        """

        _reset_testing_state()
        _reset_exception()

        _producer_thread = threading.Thread(target=self._producer_process, args=(producer, producer_config))
        _consumer_thread = threading.Thread(target=self._consumer_process, args=(consumer, consumer_config))
        _consumer_thread.daemon = True

        _consumer_thread.start()
        # Wait for consumer thread has been ready
        time.sleep(self._wait_consumer_seconds)
        _producer_thread.start()

        _producer_thread.join()

        self._final_process()


    def _producer_process(self, producer: _CrawlerProducer, producer_config: _MsgQueueConfig) -> None:
        """
        The truly usage of object **CrawlerProducer**.
        It would test for whether the exception is we define or not.

        :param producer: The *Producer* instance.
        :param producer_config: The configuration instance for *Producer*.
        :return: None
        """

        for _data_row in self.data:
            try:
                _sed_args = self._sending_argument(msg=_data_row)
                producer.run_process(config=producer_config, send_args=_sed_args)
                time.sleep(0.5)
            except Exception as e:
                if type(e) is InterruptedError:
                    assert "Stop the thread for consumer." in str(e), \
                        "The exception should be the 'InterruptedError' and content is stopping consumer thread."
                else:
                    global _Global_Testing_Exception
                    _Global_Testing_Exception = e
            else:
                self._check_producer_running_result()


    @abstractmethod
    def _sending_argument(self, msg: Union[str, bytes]) -> dict:
        """
        Generate the arguments for different *role* with *task*. It has different arguments
        with different message middle component system. So we need a argument factory to help
        us generate the arguments for its matching features.

        :param msg: A string or bytes type value. In generally, it's the message body.
        :return: A dict type value which is the arguments. So they would be use as:

                      .. code-block: python

                      _test_args = _sending_argument(msg="test")
                      function(**_test_args)

        """

        pass


    def _check_producer_running_result(self) -> None:
        """
        Check the running result of *producer* process. It does nothing here.

        :return: None
        """

        pass


    def _consumer_process(self, consumer: _CrawlerConsumer, consumer_config: _MsgQueueConfig) -> None:
        try:
            _rec_args = self._receive_argument()
            consumer.run_process(config=consumer_config, poll_args=_rec_args)
        except Exception as e:
            if type(e) is InterruptedError:
                assert "Stop the thread for consumer." in str(e), \
                    "The exception should be the 'InterruptedError' and content is stopping consumer thread."
            else:
                global _Global_Testing_Exception
                _Global_Testing_Exception = e
        else:
            self._check_consumer_running_result()


    @abstractmethod
    def _receive_argument(self) -> dict:
        """
        This is *consumer* version of *_sending_argument*. In *consumer* case, it also
        need a arguments factory to help us generate matching arguments for different features.

        :return: A dict type value which is the arguments.
        """

        pass


    def _check_consumer_running_result(self) -> None:
        """
        Check the running result of *consumer* process. it would check the counter of message queue
        and the length of list which saves message body.

        :return: None
        """

        global MessageQueueBodies, MessageQueueCnt

        assert len(MessageQueueBodies) == TestingMessageCnt - 1, f"The length of list which saves messages should be {TestingMessageCnt - 1}"
        assert MessageQueueCnt == TestingMessageCnt - 1, f"The counter of consuming messages should be {TestingMessageCnt - 1}"


    @property
    def _wait_consumer_seconds(self):
        return 3


    def _final_process(self) -> None:
        """
        The final process of the entire testing. This function would be run finally after
        it done the testing.

        :return: None
        """

        global _Global_Testing_Exception
        if _Global_Testing_Exception is not None:
            raise _Global_Testing_Exception

