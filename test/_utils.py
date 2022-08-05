
def get_rabbitmq_ip_and_port() -> [str, str]:
    """
    Getting RabbitMQ host info about IP address and port.

    :return: A tuple type value. It must be 2 values: first one is IP address and second one is port.
    """

    from ._config import RabbitMQ_Hosts
    _rabbitmq_ip, _rabbitmq_port = __parse_host_to_ip_and_port(hosts=RabbitMQ_Hosts)
    return _rabbitmq_ip, _rabbitmq_port


def get_activemq_ip_and_port() -> [str, str]:
    """
    Getting ActiveMQ host info about IP address and port.

    :return: A tuple type value. It must be 2 values: first one is IP address and second one is port.
    """

    from ._config import ActiveMQ_Hosts
    _activemq_ip, _activemq_port = __parse_host_to_ip_and_port(hosts=ActiveMQ_Hosts)
    return _activemq_ip, _activemq_port


def __parse_host_to_ip_and_port(hosts: str) -> [str, str]:
    """
    Parsing target host info to IP address and port.

    :return: A tuple type value. It must be 2 values: first one is IP address and second one is port.
    """

    if ":" not in hosts:
        raise ValueError("The format of hosts value is not correct. It should have IP and Port info, i.e., 10.10.10.10:8080.")

    _activemq_host = hosts.split(":")
    _activemq_ip = _activemq_host[0]
    _activemq_port = int(_activemq_host[1])
    return _activemq_ip, _activemq_port

