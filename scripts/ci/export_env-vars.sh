#!/usr/bin/env bash

#set -ex

env_file_path=$1
debug_mode=$2

if [ "$debug_mode" == "" ]; then
    debug_mode=false
fi

echo "Set environment variables ..."

set -o allexport
# shellcheck disable=SC1090
source "$env_file_path"

if [ "$debug_mode" == true ]; then
    echo "PYTEST_TARGET_URL_DOMAIN - $PYTEST_TARGET_URL_DOMAIN"
    echo "PYTEST_KAFKA_IP - $PYTEST_KAFKA_IP"
    echo "PYTEST_RABBITMQ_HOST - $PYTEST_RABBITMQ_HOST"
    echo "PYTEST_ACTIVEMQ_HOST - $PYTEST_ACTIVEMQ_HOST"
fi

if [ "$PYTEST_TARGET_URL_DOMAIN" == "" ]; then
    echo "It doesn't have value of environment variable 'PYTEST_TARGET_URL_DOMAIN'."
    echo "❌ Set environment variable fail."
fi

if [ "$PYTEST_KAFKA_IP" == "" ]; then
    echo "It doesn't have value of environment variable 'PYTEST_KAFKA_IP'."
    echo "❌ Set environment variable fail."
fi

if [ "$PYTEST_RABBITMQ_HOST" == "" ]; then
    echo "It doesn't have value of environment variable 'PYTEST_RABBITMQ_HOST'."
    echo "❌ Set environment variable fail."
fi

if [ "$PYTEST_ACTIVEMQ_HOST" == "" ]; then
    echo "It doesn't have value of environment variable 'PYTEST_ACTIVEMQ_HOST'."
    echo "❌ Set environment variable fail."
fi

echo "✅ Set environment variables successfully!"

