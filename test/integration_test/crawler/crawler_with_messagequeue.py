from appintegration.task.messagequeue import (
    MessageQueueConfig, MessageQueueTask,
    KafkaConfig, KafkaTask,
    RabbitMQConfig, RabbitMQTask,
    ActiveMQConfig, ActiveMQTask
)
from appintegration.crawler import AppIntegrationCrawler, MessageQueueCrawler
from appintegration.factory import ApplicationIntegrationFactory
from appintegration.arguments import ProducerArgument, ConsumerArgument
from appintegration.role import CrawlerProducer, CrawlerConsumer
from appintegration.url import OPTION_VAR_DATE, API, MessageQueueURLProducer

from ._components import RequestsHTTPRequest, RequestsStockHTTPResponseParser, ExampleWebDataHandler, DataFilePersistenceLayer, StockDataHandlerBeforeBack
from ._spec import CrawlerTestSpec

from typing import Callable, Tuple, Iterable, TypeVar, Generic, Union, cast
from pika import PlainCredentials
from abc import abstractmethod
import threading
import pytest
import random
import time
import os


_MessageQueueConfig = TypeVar("_MessageQueueConfig", bound=MessageQueueConfig)
_MessageQueueTask = TypeVar("_MessageQueueTask", bound=MessageQueueTask)

TestingMessageCnt = 3
MessageQueueCnt: int = 0
MessageQueueBodies: list = []
NewMessageQueueCnt: int = 0
NewMessageQueueBodies: list = []

_Global_Testing_Exception = None


def add_msg_cnt() -> int:
    """
    Add 1 of counter when it gets one message every times.

    :return: An integer type value which is current counter.
    """

    global MessageQueueCnt
    MessageQueueCnt += 1
    return MessageQueueCnt


def add_new_msg_cnt() -> int:
    """
    Add 1 of counter when it gets one message every times.

    :return: An integer type value which is current counter.
    """

    global NewMessageQueueCnt
    NewMessageQueueCnt += 1
    return NewMessageQueueCnt


def add_msg_queue(msg: Union[str, bytes]) -> None:
    """
    Add message object it gets into list.

    :param msg: A message object.
    :return: None
    """

    global MessageQueueBodies
    MessageQueueBodies.append(msg)


def add_new_msg_queue(msg: Union[str, bytes]) -> None:
    """
    Add message object it gets into list.

    :param msg: A message object.
    :return: None
    """

    global NewMessageQueueBodies
    NewMessageQueueBodies.append(msg)


def _reset_testing_state() -> None:
    """
    Reset all the testing states.

    :return: None
    """

    global MessageQueueCnt, MessageQueueBodies, NewMessageQueueCnt, NewMessageQueueBodies
    MessageQueueCnt = 0
    NewMessageQueueCnt = 0
    MessageQueueBodies.clear()
    NewMessageQueueBodies.clear()


def _reset_exception() -> None:
    """
    Reset the variable saves exception to be None.

    :return: None
    """

    global _Global_Testing_Exception
    _Global_Testing_Exception = None


class MessageQueueCrawlerTestSpec(CrawlerTestSpec):

    def processor_role(self) -> CrawlerConsumer:
        return CrawlerConsumer(task=self.task())


    def source_role(self) -> CrawlerProducer:
        return CrawlerProducer(task=self.task())


    @abstractmethod
    def task(self) -> Generic[_MessageQueueTask]:
        pass


    def config(self) -> Generic[_MessageQueueConfig]:
        return None


    def processor_config(self) -> Generic[_MessageQueueConfig]:
        return self.config()


    def source_config(self) -> Generic[_MessageQueueConfig]:
        return self.config()


    def new_processor_config(self) -> Generic[_MessageQueueConfig]:
        return self.config()


    @abstractmethod
    def send_arguments(self, topic, msg) -> dict:
        pass


    @abstractmethod
    def poll_arguments(self) -> dict:
        pass


    @abstractmethod
    def new_poll_arguments(self) -> dict:
        pass


    @property
    @abstractmethod
    def topic(self) -> str:
        pass


    @property
    @abstractmethod
    def new_topic(self) -> str:
        pass


    @pytest.fixture(scope="class")
    def crawler(self, factory: ApplicationIntegrationFactory) -> MessageQueueCrawler:
        return MessageQueueCrawler(factory=factory)


    def test_run_process_with_target(self, crawler: MessageQueueCrawler) -> None:

        def _test_function() -> None:
            try:
                crawler._run_process_with_target(config=self.processor_config(), poll_args=self.poll_arguments())
            except Exception as e:
                global _Global_Testing_Exception
                _Global_Testing_Exception = e

        def _checking() -> None:
            self._chk_result_of_running_process_with_target()

        self._2_threads_process(consumer_func=_test_function, consumer_args=(), checking_callable=_checking)


    def _chk_result_of_running_process_with_target(self) -> None:
        global MessageQueueBodies, MessageQueueCnt

        assert len(MessageQueueBodies) == TestingMessageCnt, f"The length of list which saves messages should be {TestingMessageCnt}"
        assert MessageQueueCnt == TestingMessageCnt, f"The counter of consuming messages should be {TestingMessageCnt}"


    def test_run(self, crawler: MessageQueueCrawler) -> None:

        def _test_function() -> None:
            try:
                crawler.run(config=self.processor_config(), poll_args=self.poll_arguments())
            except Exception as e:
                global _Global_Testing_Exception
                _Global_Testing_Exception = e

        def _checking() -> None:
            _results = crawler.run_result()
            for _body in _results:
                self._chk_result_of_running(_results=_body)

        self._2_threads_process(consumer_func=_test_function, consumer_args=(), checking_callable=_checking)


    def _chk_result_of_running(self, _results: Iterable) -> None:
        assert type(_results) is list and len(_results) != 0, "The results of crawling by method *run* should not be empty."
        for _result in _results:
            assert _result["stat"] == "OK", "The state of result should be 'OK'."
            assert "202206" in _result["date"], "The date time in result should be 2022/06/XX."
            assert _result["title"] == "111年06月 2330 台積電           各日成交資訊", "The title should be the pound of Taiwan."
            _fields = ["日期", "成交股數", "成交金額", "開盤價", "最高價", "最低價", "收盤價", "漲跌價差", "成交筆數"]
            assert random.choice(_fields) in _result["fields"], f"The field should contain one of the fields list {_fields}"
            assert type(_result["data"]) is list and len(_result["data"]) != 0, "It should have something data."
            for _data_rows in _result["data"]:
                assert len(_data_rows) == 9, "It should have something data."


    def test_run_and_save(self, crawler: MessageQueueCrawler) -> None:

        def _test_function() -> None:
            try:
                crawler.run_and_save(config=self.processor_config(), poll_args=self.poll_arguments())
            except Exception as e:
                global _Global_Testing_Exception
                _Global_Testing_Exception = e

        def _checking() -> None:
            _factory = crawler.factory
            self._chk_result_of_running_and_saving(_factory=_factory)

        self._2_threads_process(consumer_func=_test_function, consumer_args=(), checking_callable=_checking)


    def _chk_result_of_running_and_saving(self, _factory) -> None:
        _persistence_layer = cast(DataFilePersistenceLayer, _factory.persistence_factory)
        _exist = os.path.exists(_persistence_layer.file_path)
        assert _exist is True, f"It should exist a file {_persistence_layer.file_path}."
        os.remove(_persistence_layer.file_path)

        _exist = os.path.exists(_persistence_layer.file_path)
        assert _exist is False, f"It should NOT exist a file {_persistence_layer.file_path}. It should be deleted."


    def test_run_and_back_to_middle(self, crawler: MessageQueueCrawler) -> None:

        def _test_function() -> None:
            try:
                crawler.run_and_back_to_middle(
                    processor_config=self.processor_config(), poll_args=self.poll_arguments(),
                    back_config=self.source_config(), send_args=self.send_arguments(topic=self.new_topic, msg="")
                )
            except Exception as e:
                global _Global_Testing_Exception
                _Global_Testing_Exception = e

        def _checking() -> None:
            self._chk_result_of_running_and_backing_to_middle()

        self._3_threads_process(consumer_func=_test_function, consumer_args=(), checking_callable=_checking)


    def _chk_result_of_running_and_backing_to_middle(self) -> None:
        global NewMessageQueueBodies, NewMessageQueueCnt

        assert len(NewMessageQueueBodies) == TestingMessageCnt, f"The length of list which saves messages should be {TestingMessageCnt}"
        assert NewMessageQueueCnt == TestingMessageCnt, f"The counter of consuming messages should be {TestingMessageCnt}"


    def _2_threads_process(self, consumer_func: Callable, consumer_args: Tuple, checking_callable: Callable) -> None:
        _reset_testing_state()
        _reset_exception()

        _producer_thread = threading.Thread(target=self._prepare_target_data)
        _consumer_thread = threading.Thread(target=consumer_func, args=consumer_args)
        _consumer_thread.daemon = True

        _consumer_thread.start()
        # Wait for consumer thread has been ready
        time.sleep(self._wait_consumer_seconds)
        _producer_thread.start()

        # Wait for crawler running
        time.sleep(self._wait_consumer_working_seconds)

        _producer_thread.join()

        self._chk_exception()
        checking_callable()
        self._final_process()


    def _3_threads_process(self, consumer_func: Callable, consumer_args: Tuple, checking_callable: Callable) -> None:
        _reset_testing_state()
        _reset_exception()

        _producer_thread = threading.Thread(target=self._prepare_target_data)
        _consumer_thread = threading.Thread(target=consumer_func, args=consumer_args)
        _consumer_thread.daemon = True
        _new_consumer_thread = threading.Thread(target=self._new_consumer)
        _new_consumer_thread.daemon = True

        _new_consumer_thread.start()
        _consumer_thread.start()
        # Wait for consumer thread has been ready
        time.sleep(self._wait_consumer_seconds)
        _producer_thread.start()

        # Wait for crawler running
        time.sleep(self._wait_consumer_working_seconds)

        _producer_thread.join()

        self._chk_exception()
        checking_callable()
        self._final_process()


    @property
    def _wait_consumer_seconds(self) -> int:
        return 3


    @property
    def _wait_consumer_working_seconds(self) -> int:
        return 7


    def _prepare_target_data(self) -> None:
        """
        The truly usage of object **CrawlerProducer**.
        It would test for whether the exception is we define or not.

        :return: None
        """
        _target_url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={" + OPTION_VAR_DATE + "}&stockNo=2330"

        try:
            _date_urls = MessageQueueURLProducer(role=self.source_role(), base=_target_url, start="20220601", end="20220603", formatter="yyyymmdd")
            _date_urls.set_http_info(info=API())
            _date_urls.set_producer(producer_config=self.source_config(), send_args=self.send_arguments(topic=self.topic, msg=""))
            _date_urls.generate()
        except Exception as e:
            global _Global_Testing_Exception
            _Global_Testing_Exception = e


    def _new_consumer(self) -> None:
        try:
            _consumer = self.processor_role()
            _consumer.run_process(config=self.new_processor_config(), poll_args=self.new_poll_arguments())
        except Exception as e:
            global _Global_Testing_Exception
            _Global_Testing_Exception = e


    def _chk_exception(self) -> None:
        global _Global_Testing_Exception
        if _Global_Testing_Exception is not None:
            raise _Global_Testing_Exception


    def _final_process(self) -> None:
        # Sleep for 3 seconds to reduce the burdens of web site.
        time.sleep(3)



class TestMessageQueueCrawlerWithKafka(MessageQueueCrawlerTestSpec):

    def task(self) -> KafkaTask:
        return KafkaTask()


    def processor_config(self) -> KafkaConfig:
        _topics = self.topic
        return KafkaConfig(role="consumer", topics=_topics)


    def source_config(self) -> KafkaConfig:
        return KafkaConfig(role="producer")


    def new_processor_config(self) -> KafkaConfig:
        _topics = self.new_topic
        return KafkaConfig(role="consumer", topics=_topics)


    def send_arguments(self, topic: str, msg: Union[str, bytes]) -> dict:
        if type(msg) is str:
            msg = bytes(msg, "utf-8")
        return ProducerArgument.kafka(topic=topic, value=msg)


    def poll_arguments(self) -> dict:

        def _callback(msg: str) -> None:
            assert msg is not None, "The message from Kafka should NOT be empty."
            add_msg_queue(msg=msg)
            _msg_cnt = add_msg_cnt()

        return ConsumerArgument.kafka(callback=_callback)


    def new_poll_arguments(self) -> dict:

        def _callback(msg: str) -> None:
            assert msg is not None, "The message from Kafka should NOT be empty."
            add_new_msg_queue(msg=msg)
            _msg_cnt = add_new_msg_cnt()

        return ConsumerArgument.kafka(callback=_callback)


    @property
    def topic(self) -> str:
        return "test-kafka-topic"


    @property
    def new_topic(self) -> str:
        return "new-test-kafka-topic"



class TestMessageQueueCrawlerWithRabbitMQ(MessageQueueCrawlerTestSpec):

    def task(self) -> RabbitMQTask:
        return RabbitMQTask()


    def config(self) -> RabbitMQConfig:
        return RabbitMQConfig("localhost", 5672, "/", PlainCredentials("user", "password"))


    @pytest.mark.xfail(reason="It would has problem if run with other testing items.")
    def test_run_process_with_target(self, crawler: MessageQueueCrawler) -> None:
        super(TestMessageQueueCrawlerWithRabbitMQ, self).test_run_process_with_target(crawler=crawler)


    @pytest.mark.xfail(reason="It would has problem if run with other testing items.")
    def test_run_and_back_to_middle(self, crawler: MessageQueueCrawler) -> None:
        super(TestMessageQueueCrawlerWithRabbitMQ, self).test_run_and_back_to_middle(crawler=crawler)


    def _chk_result_of_running_and_backing_to_middle(self) -> None:
        global NewMessageQueueBodies, NewMessageQueueCnt
        global MessageQueueBodies, MessageQueueCnt

        print(f"[DEBUG in _chk_result_of_running_and_backing_to_middle] NewMessageQueueBodies: {NewMessageQueueBodies}")
        print(f"[DEBUG in _chk_result_of_running_and_backing_to_middle] NewMessageQueueCnt: {NewMessageQueueCnt}")
        print(f"[DEBUG in _chk_result_of_running_and_backing_to_middle] MessageQueueBodies: {MessageQueueBodies}")
        print(f"[DEBUG in _chk_result_of_running_and_backing_to_middle] MessageQueueCnt: {MessageQueueCnt}")

        assert len(NewMessageQueueBodies) > 0, f"The length of list which saves messages should be {TestingMessageCnt}"
        assert NewMessageQueueCnt > 0, f"The counter of consuming messages should be {TestingMessageCnt}"


    def send_arguments(self, topic: str, msg: Union[str, bytes]) -> dict:
        if type(msg) is str:
            msg = bytes(msg, "utf-8")
        return ProducerArgument.rabbitmq(exchange="", routing_key=topic, body=msg, default_queue=topic)


    def poll_arguments(self) -> dict:

        def _callback(ch, method, properties, body) -> None:
            assert ch is not None, "The message channel from RabbitMQ should NOT be empty."
            assert method is not None, "The message method from RabbitMQ should NOT be empty."
            assert properties is not None, "The message properties from RabbitMQ should NOT be empty."
            assert body is not None, "The message body from RabbitMQ should NOT be empty."

            add_msg_queue(msg=body)
            add_msg_cnt()

        return ConsumerArgument.rabbitmq(queue=self.topic, callback=_callback, auto_ack=True)


    def new_poll_arguments(self) -> dict:

        def _new_callback(ch, method, properties, body) -> None:
            assert ch is not None, "The message channel from RabbitMQ should NOT be empty."
            assert method is not None, "The message method from RabbitMQ should NOT be empty."
            assert properties is not None, "The message properties from RabbitMQ should NOT be empty."
            assert body is not None, "The message body from RabbitMQ should NOT be empty."

            add_new_msg_queue(msg=body)
            add_new_msg_cnt()

        return ConsumerArgument.rabbitmq(queue=self.new_topic, callback=_new_callback)


    @property
    def topic(self) -> str:
        return "test-rabbit"


    @property
    def new_topic(self) -> str:
        return "new-test-rabbit"



class TestMessageQueueCrawlerWithActiveMQ(MessageQueueCrawlerTestSpec):

    def task(self) -> ActiveMQTask:
        return ActiveMQTask()


    def config(self) -> ActiveMQConfig:
        return ActiveMQConfig([("127.0.0.1", 61613)])


    def send_arguments(self, topic: str, msg: Union[str, bytes]) -> dict:
        if type(msg) is bytes:
            msg = msg.decode("utf-8")
        return ProducerArgument.activemq(destination=topic, body=msg)


    def poll_arguments(self) -> dict:

        def _callback(frame) -> None:
            assert frame is not None, "The message from ActiveMQ should NOT be empty."
            add_msg_queue(msg=frame)
            _msg_cnt = add_msg_cnt()

        _topic = self.topic
        return ConsumerArgument.activemq(destination=_topic, callback=_callback)


    def new_poll_arguments(self) -> dict:

        def _callback(frame) -> None:
            assert frame is not None, "The message from ActiveMQ should NOT be empty."
            add_new_msg_queue(msg=frame)
            _msg_cnt = add_new_msg_cnt()

        _topic = self.new_topic
        return ConsumerArgument.activemq(destination=_topic, callback=_callback)


    @property
    def topic(self) -> str:
        return "/topic/PyTestActive"


    @property
    def new_topic(self) -> str:
        return "/topic/NewPyTestActive"

