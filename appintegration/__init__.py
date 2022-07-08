from .factory import ApplicationIntegrationFactory
from .task import (
    # For file based application integration
    CSVTask, XLSXTask, JSONTask, XMLTask, PropertiesTask,
    # For direct connect application integration
    PipeTask, SocketTask,
    # For shared database application integration
    SharedDatabaseTask,
    # For message queue application integration
    KafkaTask, RabbitMQTask, ActiveMQTask
)
from .role import (
    # For source site in application integration
    CrawlerSource, CrawlerProducer,
    # For processor site in application integration
    CrawlerProcessor, CrawlerConsumer
)
from .crawler import FileBasedCrawler, MessageQueueCrawler
