from pathlib import Path
import os


# For file based settings
Test_CSV_File_Path: str = str(Path("./for_testing.csv"))
Test_XLSX_File_Path: str = str(Path("./for_testing.xlsx"))
Test_JSON_File_Path: str = str(Path("./for_testing.json"))
Test_XML_File_Path: str = str(Path("./for_testing.xml"))
Test_PROPERTIES_File_Path: str = str(Path("./for_testing.properties"))

Test_Writing_Mode: str = "a+"
Test_XML_Writing_Mode: str = "wb"
Test_Reading_Mode: str = "r"


# For message queue settings
"""
The Kafka brokers IP (ONLY IP, NO Port)
"""
Kafka_IPs = os.getenv("PYTEST_KAFKA_IP", "localhost")
if ":" in Kafka_IPs:
    raise ValueError("The format of 'PYTEST_KAFKA_IP' is not correct. It should only IP info, NO any others like port.")

"""
RabbitMQ settings

* Hosts: IP and Port. Multiple hosts could be separated by comma, i.e., 10.10.10.10:8080,10.10.10.20:8080.
* Virtual Host: The path of virtual host. 
* Username: Username.
* Password: Password.
"""
RabbitMQ_Hosts = os.getenv("PYTEST_RABBITMQ_HOST", "localhost:5672")
if ":" not in RabbitMQ_Hosts:
    raise ValueError("The format of 'PYTEST_RABBITMQ_HOST' is not correct. It should have IP and Port info, i.e., 10.10.10.10:8080.")
RabbitMQ_Virtual_Host = os.getenv("PYTEST_RABBITMQ_VIRTUAL_HOST", "/")
RabbitMQ_Username = os.getenv("PYTEST_RABBITMQ_USERNAME", "user")
RabbitMQ_Password = os.getenv("PYTEST_RABBITMQ_PASSWORD", "password")

"""
ActiveMQ settings
 
* Hosts: IP and Port. Multiple hosts could be separated by comma, i.e., 10.10.10.10:8080,10.10.10.20:8080.
"""
ActiveMQ_Hosts = os.getenv("PYTEST_ACTIVEMQ_HOST", "127.0.0.1:61613")
if ":" not in ActiveMQ_Hosts:
    raise ValueError("The format of 'PYTEST_ACTIVEMQ_HOST' is not correct. It should have IP and Port info, i.e., 10.10.10.10:8080.")


class DummyObj:

    def __str__(self):
        return "DummyObj"

    def __repr__(self):
        return self.__str__()

    @property
    def attr(self) -> str:
        return "testing_attribute"


Test_HTTP_Parameters = {"date": "20220625", "code": "6666"}
Test_HTTP_Body = str(DummyObj())
Test_HTTP_Content_Type = "application/json"
