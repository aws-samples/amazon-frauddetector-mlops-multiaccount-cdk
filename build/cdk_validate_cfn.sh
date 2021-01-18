#!/usr/bin/env bash
set -e

echo Running with arguments $*

artifactsdir=${1:-cdkartifacts.zip}
echo artifactszip is $artifactsdir

# Set up virtual env
VIRTUAL_ENV=cdk_testvenv
virtualenv -p python3 $VIRTUAL_ENV
. $VIRTUAL_ENV/bin/activate

#Install requirements
pip install -r infra/src/requirements.txt

##Run tests
export PYTHONPATH=./infra/src

cdk --app  "python ./infra/src/app.py --configfile build/ml_pipeline_config.sample.json" synth

#Zip artifacts
echo running copy cdk out
mkdir -p $artifactsdir
cp -r cdk.out/* $artifactsdir
ls -lr $artifactsdir

# Deactivate virtual envs
deactivate
