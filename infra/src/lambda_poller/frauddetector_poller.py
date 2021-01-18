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

import boto3

from base_poller import BasePoller


class FrauddetectorPoller(BasePoller):

    def poll_training_status(self, job_parameters, client=None):
        result_is_job_complete = False
        client = client or boto3.client('frauddetector')

        training_job_name = job_parameters['training_job_name']
        training_job_version = job_parameters['training_job_version']

        response = client.get_model_version(modelId=training_job_name,
                                            modelType='ONLINE_FRAUD_INSIGHTS',
                                            modelVersionNumber=training_job_version)
        training_job_status = response["status"]
        print(response)

        # Flag CodePipeline status
        if training_job_status == 'TRAINING_COMPLETE':
            result_is_job_complete = True

        elif training_job_status == 'ERROR':
            raise Exception(f'Training job: {training_job_name} failed {response}')

        return result_is_job_complete
