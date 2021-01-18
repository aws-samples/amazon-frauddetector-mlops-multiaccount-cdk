# ***************************************************************************************
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                    *
#                                                                                       *
# Permission is hereby granted, free of charge, to any person obtaining a copy of this  *
# software and associated documentation files (the "Software"), to deal in the Software *
# without restriction, including without limitation the rights to use, copy, modify,    *
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to    *
# permit persons to whom the Software is furnished to do so.                            *
#                                                                                       *
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,   *
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A         *
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT    *
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION     *
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE        *
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                *
# ***************************************************************************************

import json

import boto3

from frauddetector_poller import FrauddetectorPoller


def lambda_handler(event, context):
    """
    This Lambda strategy relies on CodePipeline to poll the SageMaker or Fraud Detector for training job status.
    The mechanism uses the CodePipeline 'continuationToken' which tells CodePipeline to keep polling this lambda
    every 30 seconds until the logic determines that the SageMaker/FraudDetector job is either completed or
    failed.

    There is a default 24hrs executation limit on CodePipeline when using a Lambda strategy. After 24hrs,
    this CodePipeline step will automatically be flags as failed.

    :param event:
    :param context:
    :return:
    """
    # Check to make sure it is called by CodePipeline
    if 'CodePipeline.job' not in event:
        raise ValueError("This lambda function is meant to be invoked by code pipeline only")

    job_id = event['CodePipeline.job'].get('id')
    try:
        job_data = event['CodePipeline.job'].get('data')

        # Check for the continuationToken
        if 'continuationToken' in job_data:
            continuation_token = job_data['continuationToken']
            update_poll_status(job_id, continuation_token)
        # No continuationToken
        else:
            user_params = job_data.get('actionConfiguration').get('configuration').get('UserParameters')
            put_continuation_token(job_id, user_params)
    except Exception as e:
        code_pipeline = boto3.client('codepipeline')
        code_pipeline.put_job_failure_result(jobId=job_id, failureDetails={
            'type': 'JobFailed',
            'message': f'Training job:  failed. Reason: {e} for user params {event}'
        })


def put_continuation_token(job_id: str, user_parameters: str):
    """
Puts continuation token for the jobid.
    :param job_id: The job id
    :param user_parameters: A json formatted string of user params
    """
    code_pipeline = boto3.client('codepipeline')

    training_type = json.loads(user_parameters)['training_type']
    # Start polling if we know the job name
    if training_type is not None:
        code_pipeline.put_job_success_result(jobId=job_id, continuationToken=user_parameters)
    # Flag error if 'training_job_name' is not supplied
    else:
        print('No "training_type" in CodePipeline parameter. Cannot check job status. {}'.format(user_parameters))
        code_pipeline.put_job_failure_result(jobId=job_id, failureDetails={
            'type': 'JobFailed',
            'message': 'Unable to check job. No "training_job_name" in CodePipeline parameter.'
        })


def update_poll_status(job_id, continuation_token):
    """
Updates the polling status for the given job
    :param job_id:
    :param continuation_token:
    """
    type_processor_map = {
        "frauddetector": FrauddetectorPoller()
    }

    job_parameters = json.loads(continuation_token)
    training_type = job_parameters['training_type']

    # Validate job type
    assert training_type in list(type_processor_map.keys()), "The training type must be in {} ".format(
        list(type_processor_map.keys()))

    # Update polling status in code pipeline
    code_pipeline = boto3.client('codepipeline')

    try:
        # Get poller
        poller = type_processor_map[training_type]

        # Construct boto3 client
        role = job_parameters['assume_role']
        access_key, secret_key, session_token = get_credentials_for_role(role)
        client = boto3.client(
            training_type,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token,
        )

        # Check status
        is_complete = poller.poll_training_status(job_parameters, client)
        if is_complete:
            code_pipeline.put_job_success_result(jobId=job_id)
        else:
            code_pipeline.put_job_success_result(jobId=job_id, continuationToken=continuation_token)

    except Exception as e:
        code_pipeline.put_job_failure_result(jobId=job_id, failureDetails={
            'type': 'JobFailed',
            'message': f'Training job:  failed. Reason: {e} for user params {continuation_token}'
        })


def get_credentials_for_role(role_arn: str) -> (str, str, str):
    """
    Returns the temporary credentials for a job
    :param role_arn:
    :return: A tuple of access_key, secret_key, session_token
    """
    sts_connection = boto3.client('sts')
    acct_b = sts_connection.assume_role(
        RoleArn=role_arn,
        RoleSessionName="cross_acct_lambda"
    )
    access_key = acct_b['Credentials']['AccessKeyId']
    secret_key = acct_b['Credentials']['SecretAccessKey']
    session_token = acct_b['Credentials']['SessionToken']
    return access_key, secret_key, session_token
