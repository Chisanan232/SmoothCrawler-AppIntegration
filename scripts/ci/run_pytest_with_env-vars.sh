#!/usr/bin/env bash

#set -ex

test_items_path=$1
env_file_path=$2

bash scripts/ci/export_env-vars.sh "$env_file_path"

pytest "$test_items_path"
