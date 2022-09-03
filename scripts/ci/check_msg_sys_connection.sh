#!/usr/bin/env bash

#set -ex

waiting_time=$1
sleep_time=$2

if [ "$waiting_time" == "" ]; then
    waiting_time=10
fi

if [ "$sleep_time" == "" ]; then
    sleep_time=5
fi

declare IP_Address
declare Port
split_host_to_ip_and_port() {
    host_info=$1
    IFS=':' read -ra ip_addr_and_port <<< "$host_info"
    IP_Address="${ip_addr_and_port[0]}"
    Port="${ip_addr_and_port[1]}"
}

check_connection() {
    _service_name=$1
    _service_ip=$2
    _service_port=$3

    # shellcheck disable=SC2006
    for i in `seq 1 "$waiting_time"`;
    do
        nc -z "$_service_ip" "$_service_port" && echo "✅ 🎊 Success" && exit 0
        echo "The service isn't ready, it would sleep for $sleep_time seconds for waiting ..."
        echo -n .
        sleep "$sleep_time"
    done
    echo "❌ 🚫 Failed waiting for $_service_name" && exit 1
}

echo "👨‍⚕️🔬 Start to check Zookeeper connection ..."
check_connection "Zookeeper" "$kafka_ip" 2181

echo "👨‍⚕️🔬 Start to check Kafka connection ..."
kafka_ip=$PYTEST_KAFKA_IP
check_connection "Kafka" "$kafka_ip" 9092

echo "👨‍⚕️🔬 Start to check RabbitMQ connection ..."
rabbitmq_host=$PYTEST_RABBITMQ_HOST
split_host_to_ip_and_port "$rabbitmq_host"
check_connection "RabbitMQ" "$IP_Address" "$Port"

echo "👨‍⚕️🔬 Start to check ActiveMQ connection ..."
activemq_host=$PYTEST_ACTIVEMQ_HOST
split_host_to_ip_and_port "$activemq_host"
check_connection "ActiveMQ" "$IP_Address" "$Port"

echo "🎉 🍻 All tasks done!"
