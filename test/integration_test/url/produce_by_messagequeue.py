from smoothcrawler_appintegration.task.messagequeue import MessageQueueTask, MessageQueueConfig, KafkaConfig, RabbitMQConfig, ActiveMQConfig
from smoothcrawler_appintegration.arguments import ProducerArgument, ConsumerArgument
from smoothcrawler_appintegration.url import API, MessageQueueURLProducer
from smoothcrawler_appintegration import CrawlerConsumer, CrawlerProducer, KafkaTask, RabbitMQTask, ActiveMQTask

from ..._config import (
    Kafka_IPs,
    RabbitMQ_Virtual_Host, RabbitMQ_Username, RabbitMQ_Password
)
from ..._utils import MessageQueueSystemHost
from ._spec import ApplicationIntegrationURLTestSpec

from smoothcrawler.urls import OPTION_VAR_DATE
from typing import Iterable, TypeVar, Generic, Union
from abc import abstractmethod
import threading
import traceback
import pytest
import pika
import json


_MessageQueueConfig = TypeVar("_MessageQueueConfig", bound=MessageQueueConfig)
_MessageQueueTask = TypeVar("_MessageQueueTask", bound=MessageQueueTask)


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


class MessageQueueURLProducerTestSpec(ApplicationIntegrationURLTestSpec):

    _API_Info = None

    @pytest.fixture(scope="class")
    def url(self) -> MessageQueueURLProducer:
        _target_url = "http:www.test.com?date={" + OPTION_VAR_DATE + "}"
        _role = self.role(task=self.task())

        _date_urls = MessageQueueURLProducer(role=_role, base=_target_url, start="20220601", end="20220603", formatter="yyyymmdd")
        _date_urls.set_http_info(info=self.api_info)

        return _date_urls


    def role(self, task: MessageQueueTask) -> CrawlerProducer:
        return CrawlerProducer(task=task)


    @abstractmethod
    def task(self) -> Generic[_MessageQueueTask]:
        pass


    @property
    @abstractmethod
    def config(self) -> Generic[_MessageQueueConfig]:
        pass


    @property
    def api_info(self) -> API:
        if self._API_Info is None:
            self._API_Info = API()
        return self._API_Info


    @property
    @abstractmethod
    def topic(self) -> str:
        pass


    @property
    @abstractmethod
    def arguments(self) -> dict:
        pass


    def test_set_producer(self, url: MessageQueueURLProducer) -> None:
        url.set_producer(producer_config=self.config, send_args=self.arguments)


    def test_producer_config(self, url: MessageQueueURLProducer) -> None:
        _producer_config = url.producer_config
        assert _producer_config, ""


    def test_send_args(self, url: MessageQueueURLProducer) -> None:
        _send_args = url.send_args
        assert _send_args, ""


    def _chk_format_data_running_result(self, urls: Iterable[str]) -> None:
        assert type(urls) is list, ""
        for _url in urls:
            try:
                _json_data = json.loads(_url)
            except Exception:
                assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
            else:
                _json_data_key = _json_data.keys()
                assert _json_data_key == self.api_info._API_Info.keys(), "The keys of JSON type data from message queue system should be same as object *API*."


    def test_generate(self, url: MessageQueueURLProducer) -> None:

        def _generate_process() -> None:
            try:
                url.generate()
            except Exception as e:
                global _Global_Testing_Exception
                _Global_Testing_Exception = e

        _reset_exception()

        _producer_thread = threading.Thread(target=_generate_process)
        _consumer_thread = threading.Thread(target=self._consumer_process)
        _consumer_thread.daemon = True

        _consumer_thread.start()
        _producer_thread.start()

        _producer_thread.join()

        self._final_check_exception()


    @abstractmethod
    def _consumer_process(self) -> None:
        pass


    def _chk_generate_running_result(self, url_inst: MessageQueueURLProducer) -> None:
        pass


    def _final_check_exception(self) -> None:
        global _Global_Testing_Exception
        if _Global_Testing_Exception is not None:
            raise _Global_Testing_Exception



class TestURLProducerWithKafka(MessageQueueURLProducerTestSpec):

    def task(self) -> KafkaTask:
        return KafkaTask()


    @property
    def config(self) -> KafkaConfig:
        _kafka_producer_config = {
            "bootstrap_servers": Kafka_IPs
        }
        return KafkaConfig(role="producer", topics=self.topic, **_kafka_producer_config)


    @property
    def topic(self) -> str:
        return "pytest-kafka"


    @property
    def arguments(self) -> dict:
        return ProducerArgument.kafka(topic=self.topic, value=b"")


    def _consumer_process(self) -> None:

        def _callback(msg: str) -> None:
            assert msg is not None, "The message from Kafka should NOT be empty."
            add_msg_queue(msg=msg)
            _msg_cnt = add_msg_cnt()
            if _msg_cnt == TestingMessageCnt - 1:
                raise InterruptedError("Stop the thread for consumer.")

        _consumer_args = ConsumerArgument.kafka(callback=_callback)
        _consumer = CrawlerConsumer(task=self.task())
        _consumer.run_process(config=KafkaConfig(role="consumer", topics=self.topic), poll_args=_consumer_args)



class TestURLProducerWithRabbitMQ(MessageQueueURLProducerTestSpec):

    def task(self) -> RabbitMQTask:
        return RabbitMQTask()


    @property
    def config(self) -> RabbitMQConfig:
        _rabbitmq_ip, _rabbitmq_port = MessageQueueSystemHost.get_rabbitmq_ip_and_port()
        return RabbitMQConfig(_rabbitmq_ip, _rabbitmq_port, RabbitMQ_Virtual_Host, pika.PlainCredentials(RabbitMQ_Username, RabbitMQ_Password))


    @property
    def topic(self) -> str:
        return "pytest-rabbit"


    @property
    def arguments(self) -> dict:
        return ProducerArgument.rabbitmq(exchange="", routing_key=self.topic, body=b"")


    def _consumer_process(self) -> None:

        def _callback(ch, method, properties, body) -> None:
            assert ch is not None, "The message channel from RabbitMQ should NOT be empty."
            assert method is not None, "The message method from RabbitMQ should NOT be empty."
            assert properties is not None, "The message properties from RabbitMQ should NOT be empty."
            assert body is not None, "The message body from RabbitMQ should NOT be empty."

            add_msg_queue(msg=body)
            _msg_cnt = add_msg_cnt()
            if _msg_cnt == TestingMessageCnt - 1:
                raise InterruptedError("Stop the thread for consumer.")

        _topic = self.topic
        _consumer_args = ConsumerArgument.rabbitmq(queue=_topic, callback=_callback, auto_ack=True)
        _consumer = CrawlerConsumer(task=self.task())
        _consumer.run_process(config=self.config, poll_args=_consumer_args)



class TestURLProducerWithActiveMQ(MessageQueueURLProducerTestSpec):

    def task(self) -> ActiveMQTask:
        return ActiveMQTask()


    @property
    def config(self) -> ActiveMQConfig:
        _activemq_ip, _activemq_port = MessageQueueSystemHost.get_activemq_ip_and_port()
        return ActiveMQConfig([(_activemq_ip, _activemq_port)])


    @property
    def topic(self) -> str:
        return "/topic/PyTestActive"


    @property
    def arguments(self) -> dict:
        return ProducerArgument.activemq(destination=self.topic, body="")


    def _consumer_process(self) -> None:

        def _callback(frame) -> None:
            assert frame is not None, "The message from Kafka should NOT be empty."
            add_msg_queue(msg=frame)
            _msg_cnt = add_msg_cnt()
            if _msg_cnt == TestingMessageCnt - 1:
                raise InterruptedError("Stop the thread for consumer.")

        _topic = self.topic
        _consumer_args = ConsumerArgument.activemq(destination=_topic, callback=_callback)
        _consumer = CrawlerConsumer(task=self.task())
        _consumer.run_process(config=self.config, poll_args=_consumer_args)

