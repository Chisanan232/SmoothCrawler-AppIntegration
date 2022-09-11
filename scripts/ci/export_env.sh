#!/usr/bin/env bash

set -ex

## Usage:
##   . ./export-env.sh ; $COMMAND
##   . ./export-env.sh ; echo ${MINIENTREGA_FECHALIMITE}

runtime_os=$1
env_file_path=$2

if echo "$runtime_os" | grep -q 'Linux'; then

  export $(grep -v '^#' "$env_file_path" | xargs -d '\n')

elif echo "$runtime_os" | grep -q 'macOS'; then

  export $(grep -v '^#' "$env_file_path" | xargs -0)

else
  echo "The $runtime_os OS is invalid."
  exit 1

fi
