_Has_Kafka: bool = None
"""The current runtime environment whether has Python package *kafka-python* or not."""
_Has_PiKa: bool = None
"""The current runtime environment whether has Python package *pika* or not."""
_Has_Stomp: bool = None
"""The current runtime environment whether has Python package *stomp.py* or not."""

try:
    import kafka
    _Has_Kafka: bool = True
except ImportError:
    _Has_Kafka: bool = False

try:
    import pika
    _Has_PiKa: bool = True
except ImportError:
    _Has_PiKa: bool = False

try:
    import stomp
    _Has_Stomp: bool = True
except ImportError:
    _Has_Stomp: bool = False


def _has_kafka_pkg() -> bool:
    """
    It returns True if the runtime environment has Python package *kafka-python*.
    The return value of this function must to be *True* so that it could active to use *Kafka* features.

    :return: A boolean type value. *True* if it has Python package *kafka-python*, or it's *False*.
    """

    global _Has_Kafka
    return _Has_Kafka


def _has_pika_pkg() -> bool:
    """
    It returns True if the runtime environment has Python package *pika*.
    The return value of this function must to be *True* so that it could active to use *RabbitMQ* features.

    :return: A boolean type value. *True* if it has Python package *pika*, or it's *False*.
    """

    global _Has_PiKa
    return _Has_PiKa


def _has_stomp_pkg() -> bool:
    """
    It returns True if the runtime environment has Python package *stomp.py*.
    The return value of this function must to be *True* so that it could active to use *ActiveMQ* features.

    :return: A boolean type value. *True* if it has Python package *stomp.py*, or it's *False*.
    """

    global _Has_Stomp
    return _Has_Stomp


from .factory import ApplicationIntegrationFactory
from .task import (
    # For file based application integration
    CSVTask, XLSXTask, JSONTask, XMLTask, PropertiesTask,
    # For direct connect application integration
    PipeTask, SocketTask,
    # For shared database application integration
    SharedDatabaseTask
)

# For message queue application integration
if _has_kafka_pkg():
    from .task import KafkaTask
if _has_pika_pkg():
    from .task import RabbitMQTask
if _has_stomp_pkg():
    from .task import ActiveMQTask

from .role import (
    # For source site in application integration
    CrawlerSource, CrawlerProducer,
    # For processor site in application integration
    CrawlerProcessor, CrawlerConsumer
)
from .crawler import FileBasedCrawler, MessageQueueCrawler
