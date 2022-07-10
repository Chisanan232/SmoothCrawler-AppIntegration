from typing import Callable, Any, Union, Optional, TypeVar, Generic
from abc import ABCMeta, abstractmethod
import time

from ..arguments import ProducerArgument, ConsumerArgument
from .. import _has_kafka_pkg, _has_pika_pkg, _has_stomp_pkg
from .framework import ApplicationIntegrationSourceTask as _SourceTask, ApplicationIntegrationProcessorTask as _ProcessorTask

try:
    # It should install this package if user want to run the object *KafkaTask*
    # command line: pip install kafka-python
    from kafka import __version__, KafkaProducer, KafkaConsumer
    from kafka.client_async import selectors
    from kafka.partitioner.default import DefaultPartitioner
    from kafka.coordinator.assignors.range import RangePartitionAssignor
    from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
    import socket
except ImportError:
    if _has_kafka_pkg() is True:
        raise ImportError(
            "Get error when import Python package *kafka*. Please make sure that it installs *kafka-python* "
            "in your runtime environment. It suggests you run command: 'pip install kafka-python'.")

try:
    # It should install this package if user want to run the object *RabbitMQTask*
    # command line: pip install pika
    from pika import BlockingConnection, ConnectionParameters, PlainCredentials, BasicProperties
except ImportError:
    if _has_pika_pkg() is True:
        raise ImportError("Get error when import Python package *pika*. Please make sure that it installs *pika* in "
                          "your runtime environment. It suggests you run command: 'pip install pika'.")

try:
    # It should install this package if user want to run the object *ActiveMQTask*
    # command line: pip install stomp.py
    from stomp import Connection10, ConnectionListener
except ImportError as e:
    if _has_stomp_pkg() is True:
        raise ImportError("Get error when import Python package *stomp*. Please make sure that it installs *stomp.py* "
                          "in your runtime environment. It suggests you run command: 'pip install stomp.py'.")



class MessageQueueConfig(metaclass=ABCMeta):

    @abstractmethod
    def generate(self, **kwargs) -> Union[dict, Any]:
        pass


    @classmethod
    @abstractmethod
    def send_arguments(cls, **kwargs) -> dict:
        pass


    @classmethod
    @abstractmethod
    def poll_arguments(cls, **kwargs) -> dict:
        pass


_MsgQueueConfig = TypeVar("_MsgQueueConfig", bound=MessageQueueConfig)


class MessageQueueConfigTypeError(TypeError):

    def __init__(self, config: object, config_type: object):
        self.__config = config
        self.__config_type = config_type

    def __str__(self):
        return f"The configuration object {self.__config} should extends {self.__config_type.__class__} and implements its rules functions."



class MessageQueueTask(_SourceTask, _ProcessorTask):

    @abstractmethod
    def init(self, config: Generic[_MsgQueueConfig]) -> Any:
        pass


    def generate(self, **kwargs) -> None:
        # # Kafka arguments
        # topic: str, value: bytes, key: str = bytes(), partition=None, timestamp_ms=None

        # # RabbitMQ arguments
        # exchange: str, routing_key: str, body: bytes, default_queue: str = "", properties: BasicProperties = None, mandatory: bool = False

        # # ActiveMQ
        # destination: str, body: str, content_type: str = None, headers: dict = None, **keyword_headers

        self.send(**kwargs)


    def acquire(self, **kwargs) -> None:
        # # Kafka arguments
        # callback: Callable

        # # RabbitMQ arguments
        # queue: str, callback: Callable, auto_ack: bool = False, exclusive: bool = False, consumer_tag: Any = None, arguments: Any = None

        # # ActiveMQ
        # destination: str, callback: Callable, id: str = None, ack:str = "auto", headers: dict = None, **keyword_headers

        self.poll(**kwargs)


    @abstractmethod
    def send(self, **kwargs) -> Optional[Any]:
        pass


    @abstractmethod
    def poll(self, **kwargs) -> None:
        pass


    @abstractmethod
    def generate_poll_callable(self, callback: Callable) -> Callable:
        pass


    @staticmethod
    def _chk_config(__config: object, __class: Any):
        if __config is not None and isinstance(__config, __class) is False:
            raise MessageQueueConfigTypeError(config=__config, config_type=__class)



if _has_kafka_pkg():
    """
    It would active and initial the classes *KafkaConfig* and *KafkaTask* if the Python package 
    *kafka-python* exists. Or it won't do it absolutely. 
    """

    class KafkaConfig(MessageQueueConfig):

        # Default producer config
        KAFKA_PRODUCER_DEFAULT_CONFIG = {
            'bootstrap_servers': 'localhost',
            'client_id': None,
            'key_serializer': None,
            'value_serializer': None,
            'acks': 1,
            'bootstrap_topics_filter': set(),
            'compression_type': None,
            'retries': 0,
            'batch_size': 16384,
            'linger_ms': 0,
            'partitioner': DefaultPartitioner(),
            'buffer_memory': 33554432,
            'connections_max_idle_ms': 9 * 60 * 1000,
            'max_block_ms': 60000,
            'max_request_size': 1048576,
            'metadata_max_age_ms': 300000,
            'retry_backoff_ms': 100,
            'request_timeout_ms': 30000,
            'receive_buffer_bytes': None,
            'send_buffer_bytes': None,
            'socket_options': [(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)],
            'sock_chunk_bytes': 4096,  # undocumented experimental option
            'sock_chunk_buffer_count': 1000,  # undocumented experimental option
            'reconnect_backoff_ms': 50,
            'reconnect_backoff_max_ms': 1000,
            'max_in_flight_requests_per_connection': 5,
            'security_protocol': 'PLAINTEXT',
            'ssl_context': None,
            'ssl_check_hostname': True,
            'ssl_cafile': None,
            'ssl_certfile': None,
            'ssl_keyfile': None,
            'ssl_crlfile': None,
            'ssl_password': None,
            'ssl_ciphers': None,
            'api_version': None,
            'api_version_auto_timeout_ms': 2000,
            'metric_reporters': [],
            'metrics_num_samples': 2,
            'metrics_sample_window_ms': 30000,
            'selector': selectors.DefaultSelector,
            'sasl_mechanism': None,
            'sasl_plain_username': None,
            'sasl_plain_password': None,
            'sasl_kerberos_service_name': 'kafka',
            'sasl_kerberos_domain_name': None,
            'sasl_oauth_token_provider': None
        }

        # Default consumer config
        KAFKA_CONSUMER_DEFAULT_CONFIG = {
            'bootstrap_servers': 'localhost',
            'client_id': 'kafka-python-' + __version__,
            'group_id': None,
            'key_deserializer': None,
            'value_deserializer': None,
            'fetch_max_wait_ms': 500,
            'fetch_min_bytes': 1,
            'fetch_max_bytes': 52428800,
            'max_partition_fetch_bytes': 1 * 1024 * 1024,
            'request_timeout_ms': 305000,  # chosen to be higher than the default of max_poll_interval_ms
            'retry_backoff_ms': 100,
            'reconnect_backoff_ms': 50,
            'reconnect_backoff_max_ms': 1000,
            'max_in_flight_requests_per_connection': 5,
            'auto_offset_reset': 'latest',
            'enable_auto_commit': True,
            'auto_commit_interval_ms': 5000,
            'default_offset_commit_callback': lambda offsets, response: True,
            'check_crcs': True,
            'metadata_max_age_ms': 5 * 60 * 1000,
            'partition_assignment_strategy': (RangePartitionAssignor, RoundRobinPartitionAssignor),
            'max_poll_records': 500,
            'max_poll_interval_ms': 300000,
            'session_timeout_ms': 10000,
            'heartbeat_interval_ms': 3000,
            'receive_buffer_bytes': None,
            'send_buffer_bytes': None,
            'socket_options': [(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)],
            'sock_chunk_bytes': 4096,  # undocumented experimental option
            'sock_chunk_buffer_count': 1000,  # undocumented experimental option
            'consumer_timeout_ms': float('inf'),
            'security_protocol': 'PLAINTEXT',
            'ssl_context': None,
            'ssl_check_hostname': True,
            'ssl_cafile': None,
            'ssl_certfile': None,
            'ssl_keyfile': None,
            'ssl_crlfile': None,
            'ssl_password': None,
            'ssl_ciphers': None,
            'api_version': None,
            'api_version_auto_timeout_ms': 2000,
            'connections_max_idle_ms': 9 * 60 * 1000,
            'metric_reporters': [],
            'metrics_num_samples': 2,
            'metrics_sample_window_ms': 30000,
            'metric_group_prefix': 'consumer',
            'selector': selectors.DefaultSelector,
            'exclude_internal_topics': True,
            'sasl_mechanism': None,
            'sasl_plain_username': None,
            'sasl_plain_password': None,
            'sasl_kerberos_service_name': 'kafka',
            'sasl_kerberos_domain_name': None,
            'sasl_oauth_token_provider': None,
            'legacy_iterator': False,  # enable to revert to < 1.4.7 iterator
        }


        def __init__(self, role: str, topics: Union[str, tuple] = "", **kwargs):
            self._role = role
            self._topics = topics
            self._config = kwargs


        def generate(self) -> dict:
            if self._role == "producer":
                self.KAFKA_PRODUCER_DEFAULT_CONFIG.update(**self._config)
                return self.KAFKA_PRODUCER_DEFAULT_CONFIG
            elif self._role == "consumer":
                self.KAFKA_CONSUMER_DEFAULT_CONFIG.update(**self._config)
                return self.KAFKA_CONSUMER_DEFAULT_CONFIG
            else:
                raise ValueError


        def is_producer(self) -> bool:
            return self._role == "producer"


        def is_consumer(self) -> bool:
            return self._role == "consumer"


        def topics(self) -> Union[str, tuple]:
            return self._topics


        @classmethod
        def send_arguments(cls, topic: str, value: Union[str, bytes], key: str = bytes(), partition=None, timestamp_ms=None) -> dict:
            if type(value) is str:
                value = bytes(value, "utf-8")
            return ProducerArgument.kafka(topic=topic, value=value, key=key, partition=partition, timestamp_ms=timestamp_ms)


        @classmethod
        def poll_arguments(cls, callback: Callable) -> dict:
            return ConsumerArgument.kafka(callback=callback)



    class KafkaTask(MessageQueueTask):

        _Config: dict = None
        _Kafka_App: Union[KafkaProducer, KafkaConsumer] = None

        def init(self, config: KafkaConfig) -> Any:
            # Initial Kafka components configuration
            MessageQueueTask._chk_config(config, KafkaConfig)
            self._Config = config.generate()

            assert config.is_producer() or config.is_consumer(), "It must be producer or consumer."

            if config.is_producer():
                self._Kafka_App = KafkaProducer(**self._Config)
            elif config.is_consumer():
                _topics = config.topics()
                self._Kafka_App = KafkaConsumer(_topics, **self._Config)


        def send(self, topic: str, value: bytes, key: str = None, partition=None, timestamp_ms=None) -> None:
            self._Kafka_App.send(topic=topic, value=value, key=key, partition=partition, timestamp_ms=timestamp_ms)


        def poll(self, callback: Callable, **kwargs) -> None:
            for _msg in self._Kafka_App:
                callback(msg=_msg)


        def generate_poll_callable(self, callback: Callable) -> Callable:
            """
            Below is an example how it gets message from Kafka:

                ConsumerRecord(topic='test-kafka-topic', partition=0, offset=91, timestamp=1656752880320, timestamp_type=0, key=b'', value=b'{"http_method": "GET", "url": "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=20220602&stockNo=2330", "parameters": {}, "body": null, "content_type": null}', headers=[], checksum=None, serialized_key_size=0, serialized_value_size=176, serialized_header_size=-1)

            :param callback:
            :return:
            """

            def _kafka_callback(msg) -> Any:
                return callback(target=msg.value)

            return _kafka_callback


        def close(self) -> None:
            pass



if _has_pika_pkg():
    """
    It would active and initial the classes *RabbitConfig* and *RabbitTask* if the Python package 
    *pika* exists. Or it won't do it absolutely. 
    """

    class RabbitMQConfig(MessageQueueConfig):

        Default_RabbitMQ_Config: dict = {
            "host": None,
            "port": None,
            "virtual_host": None,
            "credentials": None,
            "channel_max": None,
            "frame_max": None,
            "heartbeat": None,
            "ssl_options": None,
            "connection_attempts": None,
            "retry_delay": None,
            "socket_timeout": None,
            "stack_timeout": None,
            "locale": None,
            "blocked_connection_timeout": None,
            "client_properties": None,
            "tcp_options": None
        }

        _DEFAULT = ConnectionParameters._DEFAULT

        def __init__(self, host=_DEFAULT,
                     port=_DEFAULT,
                     virtual_host=_DEFAULT,
                     credentials=_DEFAULT,
                     channel_max=_DEFAULT,
                     frame_max=_DEFAULT,
                     heartbeat=_DEFAULT,
                     ssl_options=_DEFAULT,
                     connection_attempts=_DEFAULT,
                     retry_delay=_DEFAULT,
                     socket_timeout=_DEFAULT,
                     stack_timeout=_DEFAULT,
                     locale=_DEFAULT,
                     blocked_connection_timeout=_DEFAULT,
                     client_properties=_DEFAULT,
                     tcp_options=_DEFAULT):

            self.Default_RabbitMQ_Config.update({
                "host": host,
                "port": port,
                "virtual_host": virtual_host,
                "credentials": credentials,
                "channel_max": channel_max,
                "frame_max": frame_max,
                "heartbeat": heartbeat,
                "ssl_options": ssl_options,
                "connection_attempts": connection_attempts,
                "retry_delay": retry_delay,
                "socket_timeout": socket_timeout,
                "stack_timeout": stack_timeout,
                "locale": locale,
                "blocked_connection_timeout": blocked_connection_timeout,
                "client_properties": client_properties,
                "tcp_options": tcp_options
            })


        def generate(self, **kwargs) -> ConnectionParameters:
            return ConnectionParameters(**self.Default_RabbitMQ_Config)


        @classmethod
        def send_arguments(cls, exchange: str, routing_key: str, body: Union[str, bytes], default_queue: str = "", properties: BasicProperties = None, mandatory: bool = False) -> dict:
            if type(body) is str:
                body = bytes(body, "utf-8")
            return ProducerArgument.rabbitmq(exchange=exchange, routing_key=routing_key, body=body, default_queue=default_queue, properties=properties, mandatory=mandatory)


        @classmethod
        def poll_arguments(cls, queue: str, callback: Callable, auto_ack: bool = False, exclusive: bool = False, consumer_tag: Any = None, arguments: Any = None) -> dict:
            return ConsumerArgument.rabbitmq(queue=queue, callback=callback, auto_ack=auto_ack, exclusive=exclusive, consumer_tag=consumer_tag, arguments=arguments)



    class RabbitMQTask(MessageQueueTask):

        _Config: ConnectionParameters = None
        _Connection = None
        _Channel = None

        def init(self, config: RabbitMQConfig) -> Any:
            MessageQueueTask._chk_config(config, RabbitMQConfig)
            self._Config = config.generate()

            self._Connection = BlockingConnection(parameters=self._Config)
            self._Channel = self._Connection.channel()


        def _declare_queue(self, queue: str, passive: bool = False, durable: bool = False, exclusive: bool = False, auto_delete: bool = False, arguments: Any = None) -> None:
            # Only for RabbitMQ
            # Define a message queue in RabbitMQ
            self._Channel.queue_declare(queue=queue, passive=passive, durable=durable, exclusive=exclusive, auto_delete=auto_delete, arguments=arguments)


        def _bind_queue(self, queue: str, exchange: str, routing_key: str = None, arguments: dict = None) -> None:
            self._Channel.queue_bind(queue=queue, exchange=exchange, routing_key=routing_key, arguments=arguments)


        def send(self, exchange: str, routing_key: str, body: bytes, default_queue: str = "", properties: BasicProperties = None, mandatory: bool = False) -> None:
            self._declare_queue(queue=default_queue)
            # self._bind_queue(queue=default_queue, exchange=exchange, routing_key=routing_key)

            self._Channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body, properties=properties, mandatory=mandatory)


        def poll(self, queue: str, callback: Callable, auto_ack: bool = False, exclusive: bool = False, consumer_tag: Any = None, arguments: Any = None) -> None:
            self._declare_queue(queue=queue)
            # self._bind_queue(queue=queue, exchange="")

            self._Channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=auto_ack, exclusive=exclusive, consumer_tag=consumer_tag, arguments=arguments)
            self._Channel.start_consuming()


        def generate_poll_callable(self, callback: Callable) -> Callable:

            def _rabbitmq_callback(ch, method, properties, body) -> Any:
                return callback(target=body)

            return _rabbitmq_callback


        def close(self) -> None:
            self._Channel.close()



if _has_stomp_pkg():
    """
    It would active and initial the classes *ActiveMQConfig* and *ActiveMQTask* if the Python package 
    *stomp.py* exists. Or it won't do it absolutely. 
    """

    class ActiveMQConfig(MessageQueueConfig):

        _Default_Config: dict = {
            "host_and_ports": None,
            "prefer_localhost": True,
            "try_loopback_connect": True,
            "reconnect_sleep_initial": 0.1,
            "reconnect_sleep_increase": 0.5,
            "reconnect_sleep_jitter": 0.1,
            "reconnect_sleep_max": 60.0,
            "reconnect_attempts_max": 3,
            "timeout": None,
            "keepalive": None,
            "auto_decode": True,
            "encoding": "utf-8",
            "auto_content_length": True,
            "bind_host_port": None
        }

        def __init__(self,
                     host_and_ports=None,
                     prefer_localhost=True,
                     try_loopback_connect=True,
                     reconnect_sleep_initial=0.1,
                     reconnect_sleep_increase=0.5,
                     reconnect_sleep_jitter=0.1,
                     reconnect_sleep_max=60.0,
                     reconnect_attempts_max=3,
                     timeout=None,
                     keepalive=None,
                     auto_decode=True,
                     encoding="utf-8",
                     auto_content_length=True,
                     bind_host_port=None):

            self._Default_Config.update({
                "host_and_ports": host_and_ports,
                "prefer_localhost": prefer_localhost,
                "try_loopback_connect": try_loopback_connect,
                "reconnect_sleep_initial": reconnect_sleep_initial,
                "reconnect_sleep_increase": reconnect_sleep_increase,
                "reconnect_sleep_jitter": reconnect_sleep_jitter,
                "reconnect_sleep_max": reconnect_sleep_max,
                "reconnect_attempts_max": reconnect_attempts_max,
                "timeout": timeout,
                "keepalive": keepalive,
                "auto_decode": auto_decode,
                "encoding": encoding,
                "auto_content_length": auto_content_length,
                "bind_host_port": bind_host_port
            })


        def generate(self, **kwargs) -> dict:
            return self._Default_Config


        @classmethod
        def send_arguments(cls, destination: str, body: str, content_type: str = None, headers: dict = None, **keyword_headers) -> dict:
            return ProducerArgument.activemq(destination=destination, body=body, content_type=content_type, headers=headers, **keyword_headers)


        @classmethod
        def poll_arguments(cls, destination: str, callback: Callable, id: str = None, ack: str = "auto", headers: dict = None, **keyword_headers) -> dict:
            return ConsumerArgument.activemq(destination=destination, callback=callback, id=id, ack=ack, headers=headers, **keyword_headers)



    class ActiveMQTask(MessageQueueTask):

        _Config: dict = None
        _Connection = None

        def init(self, config: ActiveMQConfig) -> Any:
            MessageQueueTask._chk_config(config, ActiveMQConfig)
            self._Config = config.generate()

            self._Connection = Connection10(**self._Config)
            self._Connection.connect()


        def send(self, destination: str, body: str, content_type: str = None, headers: dict = None, **keyword_headers) -> None:
            self._Connection.send(destination=destination, body=body, content_type=content_type, headers=headers, **keyword_headers)


        def poll(self, destination: str, callback: Callable, id: str = None, ack: str = "auto", headers: dict = None, **keyword_headers) -> None:

            class _Listener(ConnectionListener):

                def on_message(self, frame) -> None:
                    callback(frame)

            self._Connection.set_listener(name="_Listener", listener=_Listener())
            self._Connection.subscribe(destination=destination, id=id, ack=ack, headers=headers, **keyword_headers)

            while True:
                time.sleep(5)


        def generate_poll_callable(self, callback: Callable) -> Callable:

            def _activemq_callback(frame) -> Any:
                """
                An example frame would like below:

                    {cmd=MESSAGE,headers=[{'content-length': '33', 'expires': '0', 'destination': '/queue/TestQueue', 'priority': '4', 'message-id': 'ID:fd77ea946402-32863-1655607094846-3:190:-1:1:10', 'timestamp': '1656644243261'}],body=This is testing message for time.}

                It has 3 attributes:

                    * cmd: command
                    * headers: The header info of activemq
                    * body: message body.

                :param frame: A frame object.
                :return:
                """
                return callback(target=frame.body)

            return _activemq_callback


        def close(self) -> None:
            self._Connection.disconnect()

