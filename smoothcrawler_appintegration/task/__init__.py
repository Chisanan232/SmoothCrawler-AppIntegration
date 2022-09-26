from .. import _has_kafka_pkg, _has_pika_pkg, _has_stomp_pkg
from .filebased import CSVTask, XLSXTask, JSONTask, XMLTask, PropertiesTask
# from .shareddatabase import SharedDatabaseTask
# from .directconnect import PipeTask, SocketTask

if _has_kafka_pkg():
    from .messagequeue import KafkaConfig, KafkaTask
if _has_pika_pkg():
    from .messagequeue import RabbitMQConfig, RabbitMQTask
if _has_stomp_pkg():
    from .messagequeue import ActiveMQConfig, ActiveMQTask
