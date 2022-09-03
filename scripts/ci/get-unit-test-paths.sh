#!/usr/bin/env bash

set -ex
runtime_os=$1

declare -a init_tests
declare -a task_tests
declare -a role_tests
declare -a utils_file_tests

getalltests() {
    # shellcheck disable=SC2207
    declare -a testpatharray=( $(ls -F "$1" | grep -v '/$' | grep -v '__init__.py' | grep -v 'test_config.py' | grep -v -E '^_[a-z_]{1,64}.py' | grep -v '__pycache__'))

    declare -a alltestpaths
    for (( i = 0; i < ${#testpatharray[@]}; i++ )) ; do
        alltestpaths[$i]=$1${testpatharray[$i]}
    done

    if echo "$1" | grep -q "task";
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        task_tests=${alltestpaths[@]}
    elif echo "$1" | grep -q "role";
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        role_tests=${alltestpaths[@]}
    elif echo "$1" | grep -q "utils" | grep -q "file";
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        utils_file_tests=${alltestpaths[@]}
    else
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        init_tests=${alltestpaths[@]}
    fi
}

init_path=test/unit_test/
task_path=test/unit_test/task/
role_path=test/unit_test/role/
utils_file_path=test/unit_test/_utils/file/

getalltests $init_path
getalltests $task_path
getalltests $role_path
getalltests $utils_file_path

dest=( "${init_tests[@]} ${task_tests[@]} ${role_tests[@]} ${utils_file_tests[@]}" )


if echo "$runtime_os" | grep -q "windows";
then
    printf "${dest[@]}" | jq -R .
elif echo "$runtime_os" | grep -q "unix";
then
    printf '%s\n' "${dest[@]}" | jq -R . | jq -cs .
else
    printf 'error' | jq -R .
fi
