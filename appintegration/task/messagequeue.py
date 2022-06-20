from typing import Callable, Any, Union, Optional, TypeVar, Generic
from abc import ABCMeta, abstractmethod
import time

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
    pass

try:
    # It should install this package if user want to run the object *RabbitMQTask*
    # command line: pip install pika
    from pika import BlockingConnection, ConnectionParameters, PlainCredentials, BasicProperties
except ImportError:
    pass

try:
    # It should install this package if user want to run the object *ActiveMQTask*
    # command line: pip install stomp.py
    from stomp import Connection10, ConnectionListener
except ImportError:
    pass

from .framework import ApplicationIntegrationSourceTask as _SourceTask, ApplicationIntegrationProcessorTask as _ProcessorTask



class MessageQueueConfig(metaclass=ABCMeta):

    @abstractmethod
    def generate(self, **kwargs) -> Union[dict, Any]:
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
    def init(self, config: Generic[_MsgQueueConfig], **kwargs) -> Any:
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


    @staticmethod
    def _chk_config(__config: object, __class: Any):
        if __config is not None and isinstance(__config, __class) is False:
            raise MessageQueueConfigTypeError(config=__config, config_type=__class)



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


    def __init__(self, role: str, **kwargs):
        self._role = role
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



class KafkaTask(MessageQueueTask):

    _Config: dict = None
    _Kafka_App: Union[KafkaProducer, KafkaConsumer] = None

    def init(self, config: KafkaConfig, **kwargs) -> Any:
        # Initial Kafka components configuration
        MessageQueueTask._chk_config(config, KafkaConfig)
        self._Config = config.generate()

        assert config.is_producer() or config.is_consumer(), ""

        if config.is_producer():
            self._Kafka_App = KafkaProducer(**self._Config)
        elif config.is_consumer():
            _topics = kwargs.get("topics")
            self._Kafka_App = KafkaConsumer(_topics, **self._Config)


    def send(self, topic: str, value: bytes, key: str = None, partition=None, timestamp_ms=None) -> None:
        self._Kafka_App.send(topic=topic, value=value, key=key, partition=partition, timestamp_ms=timestamp_ms)


    def poll(self, callback: Callable, **kwargs) -> None:
        for _msg in self._Kafka_App:
            callback(msg=_msg)


    def close(self) -> None:
        pass



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



class RabbitMQTask(MessageQueueTask):

    _Config: ConnectionParameters = None
    _Connection = None
    _Channel = None

    _Declare_Flag: bool = False

    def init(self, config: RabbitMQConfig, **kwargs) -> Any:
        MessageQueueTask._chk_config(config, RabbitMQConfig)
        self._Config = config.generate()

        self._Connection = BlockingConnection(parameters=self._Config)
        self._Channel = self._Connection.channel()


    def _declare_queue(self, queue: str, passive: bool = False, durable: bool = False, exclusive: bool = False, auto_delete: bool = False, arguments: Any = None) -> None:
        # Only for RabbitMQ
        # Define a message queue in RabbitMQ
        self._Channel.queue_declare(queue=queue, passive=passive, durable=durable, exclusive=exclusive, auto_delete=auto_delete, arguments=arguments)
        self._Declare_Flag = True


    def send(self, exchange: str, routing_key: str, body: bytes, default_queue: str = "", properties: BasicProperties = None, mandatory: bool = False) -> None:
        if self._Declare_Flag is False:
            self._declare_queue(queue=default_queue)

        self._Channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body, properties=properties, mandatory=mandatory)


    def poll(self, queue: str, callback: Callable, auto_ack: bool = False, exclusive: bool = False, consumer_tag: Any = None, arguments: Any = None) -> None:
        if self._Declare_Flag is False:
            self._declare_queue(queue=queue)

        self._Channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=auto_ack, exclusive=exclusive, consumer_tag=consumer_tag, arguments=arguments)
        self._Channel.start_consuming()


    def close(self) -> None:
        self._Channel.close()



class ActiveMQConfig(MessageQueueConfig):

    def generate(self, **kwargs) -> dict:
        pass



class ActiveMQTask(MessageQueueTask):

    _Connection = None

    def init(self, config: ActiveMQConfig, **kwargs) -> Any:
        MessageQueueTask._chk_config(config, ActiveMQConfig)

        self._Connection = Connection10([("127.0.0.1", 61613)])
        self._Connection.connect()


    def send(self, destination: str, body: str, content_type: str = None, headers: dict = None, **keyword_headers) -> None:
        self._Connection.send(destination=destination, body=body, content_type=content_type, headers=headers, **keyword_headers)


    def poll(self, destination: str, callback: Callable, id: str = None, ack:str = "auto", headers: dict = None, **keyword_headers) -> None:

        class _Listener(ConnectionListener):

            def on_message(self, frame) -> None:
                callback(frame)

        self._Connection.set_listener(name="_Listener", listener=_Listener())
        self._Connection.subscribe(destination=destination, id=id, ack=ack, headers=headers, **keyword_headers)

        while True:
            time.sleep(10)


    def close(self) -> None:
        self._Connection.disconnect()

