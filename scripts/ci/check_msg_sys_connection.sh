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

declare System_Health
check_connection() {
    _service_name=$1
    _service_ip=$2
    _service_port=$3

    # shellcheck disable=SC2006
    for i in `seq 1 "$waiting_time"`;
    do
        nc_result=$(nc -z "$_service_ip" "$_service_port")
        if echo "$nc_result" | grep -q "succeeded"; then
            echo "✅ 🎊 Success" && System_Health=true
        else
#            nc -z "$_service_ip" "$_service_port" && echo "✅ 🎊 Success" && System_Health=true
#            echo "The service isn't ready, it would sleep for $sleep_time seconds for waiting ..."
            echo -n .
            sleep "$sleep_time"
        fi
    done
    echo "❌ 🚫 Failed waiting for $_service_name" && System_Health=false
}

echo "👨‍⚕️🔬 Start to check Zookeeper connection ..."
zookeeper_ip=127.0.0.1
check_connection "Zookeeper" "$zookeeper_ip" 2181
declare Zookeeper_Health
if [ "$System_Health" == true ]; then
    Zookeeper_Health=true
fi

echo "👨‍⚕️🔬 Start to check Kafka connection ..."
kafka_ip=$PYTEST_KAFKA_IP
check_connection "Kafka" "$kafka_ip" 9092
declare Kafka_Health
if [ "$System_Health" == true ]; then
    Kafka_Health=true
fi

echo "👨‍⚕️🔬 Start to check RabbitMQ connection ..."
rabbitmq_host=$PYTEST_RABBITMQ_HOST
split_host_to_ip_and_port "$rabbitmq_host"
check_connection "RabbitMQ" "$IP_Address" "$Port"
declare RabbitMQ_Health
if [ "$System_Health" == true ]; then
    RabbitMQ_Health=true
fi

echo "👨‍⚕️🔬 Start to check ActiveMQ connection ..."
activemq_host=$PYTEST_ACTIVEMQ_HOST
split_host_to_ip_and_port "$activemq_host"
check_connection "ActiveMQ" "$IP_Address" "$Port"
declare ActiveMQ_Health
if [ "$System_Health" == true ]; then
    ActiveMQ_Health=true
fi

declare UnHealth_History=true
if [ "$Zookeeper_Health" != true ]; then
    echo "Zookeeper isn't ready for testing ..."
    UnHealth_History=false
fi
if [ "$Kafka_Health" != true ]; then
    echo "Kafka isn't ready for testing ..."
    UnHealth_History=false
fi
if [ "$RabbitMQ_Health" != true ]; then
    echo "RabbitMQ isn't ready for testing ..."
    UnHealth_History=false
fi
if [ "$ActiveMQ_Health" != true ]; then
    echo "ActiveMQ isn't ready for testing ..."
    UnHealth_History=false
fi

if [ "$UnHealth_History" == true ]; then
    echo "🎉 🍻 All tasks done and all message queue system are already for testing!" && exit 0
else
    echo "❌ 💔 Some message queue system isn't already and checking fail ..." && exit 1
fi
