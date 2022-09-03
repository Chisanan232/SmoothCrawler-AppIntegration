#!/usr/bin/env bash

set -ex
runtime_os=$1

declare -a base_tests
declare -a url_tests
declare -a role_and_task_with_filebased_tests
declare -a role_and_task_with_directconnect_tests
declare -a role_and_task_with_shareddatabase_tests
declare -a role_and_task_with_messagequeue_tests
declare -a crawler_tests

getalltests() {
    # shellcheck disable=SC2207
    declare -a testpatharray=( $(ls -F "$1" | grep -v '/$' | grep -v '__init__.py' | grep -v 'test_config.py' | grep -v -E '^_[a-z_]{1,64}.py' | grep -v '__pycache__'))

    declare -a alltestpaths
    for (( i = 0; i < ${#testpatharray[@]}; i++ )) ; do
        alltestpaths[$i]=$1${testpatharray[$i]}
    done

    if echo "$1" | grep -q "role_and_task";
    then
        if echo "$1" | grep -q "with_filebased";
        then
            # shellcheck disable=SC2124
            # shellcheck disable=SC2178
            role_and_task_with_filebased_tests=${alltestpaths[@]}
        elif echo "$1" | grep -q "with_directconnect";
        then
            # shellcheck disable=SC2124
            # shellcheck disable=SC2178
            role_and_task_with_directconnect_tests=${alltestpaths[@]}
        elif echo "$1" | grep -q "with_shareddatabase";
        then
            # shellcheck disable=SC2124
            # shellcheck disable=SC2178
            role_and_task_with_shareddatabase_tests=${alltestpaths[@]}
        elif echo "$1" | grep -q "with_messagequeue";
        then
            # shellcheck disable=SC2124
            # shellcheck disable=SC2178
            role_and_task_with_messagequeue_tests=${alltestpaths[@]}
        fi
    elif echo "$1" | grep -q "url";
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        url_tests=${alltestpaths[@]}
    elif echo "$1" | grep -q "crawler";
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        crawler_tests=${alltestpaths[@]}
    else
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        base_tests=${alltestpaths[@]}
    fi
}

base_path=test/integration_test/
url_path=test/integration_test/url/
role_with_filebased_task_path=test/integration_test/role_and_task/with_filebased/
role_with_directconnect_task_path=test/integration_test/role_and_task/with_directconnect/
role_with_shareddatabase_task_path=test/integration_test/role_and_task/with_shareddatabase/
role_with_messagequeue_task_path=test/integration_test/role_and_task/with_messagequeue/
crawler_path=test/integration_test/crawler/

getalltests $base_path
getalltests $url_path
getalltests $role_with_filebased_task_path
getalltests $role_with_directconnect_task_path
getalltests $role_with_shareddatabase_task_path
getalltests $role_with_messagequeue_task_path
getalltests $crawler_path

# shellcheck disable=SC2207
dest=( "${base_tests[@]}"`
        `" ${url_tests[@]}"`
        `" ${role_and_task_with_filebased_tests[@]}"`
        `" ${role_and_task_with_directconnect_tests[@]}"`
        `" ${role_and_task_with_shareddatabase_tests[@]}"`
        `" ${role_and_task_with_messagequeue_tests[@]}"`
        `" ${crawler_tests[@]}" )

if echo "$runtime_os" | grep -q "windows";
then
    printf '%s\n' "${dest[@]}" | jq -R .
elif echo "$runtime_os" | grep -q "unix";
then
    printf '%s\n' "${dest[@]}" | jq -R . | jq -cs .
else
    printf 'error' | jq -R .
fi
