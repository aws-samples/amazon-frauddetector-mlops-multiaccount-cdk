#!/usr/bin/env bash
set -e

echo "$@"

# Set up virtual env
VIRTUAL_ENV=$1
virtualenv -p python3 $VIRTUAL_ENV
. $VIRTUAL_ENV/bin/activate

#Install requirements
pip install -r tests/requirements.txt
pip install -r src/requirements.txt

#Run tests
export PYTHONPATH=./src
pytest --tb=short

#Run pyflakes to detect any import / syntax issues
pyflakes ./**/*.py

# Deactivate virtual envs
deactivate
