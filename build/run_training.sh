#!/usr/bin/env bash
set -e

help_msg="Usage: $0 <virtual_env_name> <role_for_fraudtecteor> <s3_bucket_training_data> [role_to_assume]"
usage_msg="e.g.\n$0 testenv arn:aws:role::test-repo s3://test/abc model"
min_args=3

if [[ $# -le ${min_args} ]] ; then
    echo "ERROR: Not all mandatory ${min_args} supplied, supplied just $# \n $*"
    echo ${help_msg}
    echo ${usage_msg}
    exit 1
fi

echo Running with arguments $*

VIRTUAL_ENV=$1
fd_data_access_role=$2
s3_trainingdata_uri=$3
role_to_assume=${4:-None}


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
python ./src/main_demo_fraud_detector_train.py --s3uri "${s3_trainingdata_uri}" --role "${fd_data_access_role}" --sampledata src/sample_data_variable_creation.csv


# Deactivate virtual envs
deactivate
