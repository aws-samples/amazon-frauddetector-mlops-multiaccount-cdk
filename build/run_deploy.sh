#!/usr/bin/env bash
set -e

help_msg="Usage: $0 <virtual_env_name> <model_name> <model_version> <detector_name> [role_to_assume]"
usage_msg="e.g.\n$0 testenv arn:aws:role::test-repo s3://test/abc model"
min_args=4

if [[ $# -le ${min_args} ]] ; then
    echo "ERROR: Not all mandatory ${min_args} supplied, supplied just $# \n $*"
    echo ${help_msg}
    echo ${usage_msg}
    exit 1
fi

echo Running with arguments $*

VIRTUAL_ENV=$1
model_name=$2
model_version=$3
detector_name=${4}
role_to_assume=${5:None}


# Set up virtual env
. $VIRTUAL_ENV/bin/activate

# Role to assume is passed, use that..
if [ "$role_to_assume" != "None" ];
then
    echo Assuming role ${role_to_assume}
    credentials=`aws sts assume-role --role-arn "${role_to_assume}" --role-session-name AWSCLI-Session --output text`

    ACCESS_KEY=`echo $credentials | cut -f 5 -d " "`
    ACCESS_SECRET=`echo $credentials | cut -f 7 -d " "`
    SESSION_TOKEN=`echo $credentials | cut -f 8 -d " "`

    export AWS_ACCESS_KEY_ID=${ACCESS_KEY}
    export AWS_SECRET_ACCESS_KEY=${ACCESS_SECRET}
    export AWS_SESSION_TOKEN=${SESSION_TOKEN}


fi

echo `aws sts get-caller-identity`

export PYTHONPATH=./src
python ./src/main_demo_fraud_detector_deploy.py --model "${model_name}" --modelVersion "${model_version}" --detector "${detector_name}"


# Deactivate virtual envs
deactivate
