#!/usr/bin/env bash

set -ex

## Usage:
##   . ./export-env.sh ; $COMMAND
##   . ./export-env.sh ; echo ${MINIENTREGA_FECHALIMITE}

runtime_os=$1
if echo "$runtime_os" | grep -q 'ubuntu'; then

  export $(grep -v '^#' .env | xargs -d '\n')

elif echo "$runtime_os" | grep -q 'macos'; then

  export $(grep -v '^#' .env | xargs -0)

else
  echo "The $runtime_os OS is invalid."
  exit 1

fi
