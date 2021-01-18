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

import logging

import boto3
import botocore
from core.fraud_detector_utils import FraudDetectorUtils
from features.feature_variables_base import FeatureVariablesBase


class FraudDetectorTrain:

    def __init__(self, client=None, fraud_detector_utils=None):
        self.fraud_detector_utils = fraud_detector_utils or FraudDetectorUtils()
        self.client = client or boto3.client('frauddetector')

    @property
    def _logger(self):
        return logging.getLogger(__name__)

    def run(self, model_name: str, model_variables: FeatureVariablesBase, model_description: str, model_type: str,
            s3_training_file: str, role_arn: str,
            event_type_name: str, wait=False):
        """
        Run a model training job
        @param model_name: Name of the model
        @param model_variables: Type of FeatureVariablesBase , to create model variables an labels
        @param model_description: A description of the model
        @param model_type: The type of model, e.g. ONLINE_FRAUD_INSIGHTS
        @param s3_training_file: The train data file
        @param role_arn: ARN of the role
        @param wait: If true , waits for the training job to complete , else exits after kicking off the training job
        @param event_type_name: The type of event e.g. order, login etc
        @return: a dict of model name and version, e.g. {"modelVersionNumber" : "1.0", "modelId" :  "demo"}
        """

        # Create model features
        model_features = model_variables.create_or_retrieve_features()
        model_label = model_variables.create_or_retrieve_label()

        # Create / update initializes the model
        self._logger.info("Initialise model - {} ".format(model_name))
        try:
            self.client.get_models(
                modelId=model_name,
                modelType=model_type
            )
            self._logger.info("Model {} already exists ".format(model_name))
        except botocore.errorfactory.ClientError as error:
            # If resource not found, it means that the model doesnt exist, so lets create it
            if error.response['Error']['Code'] == 'ResourceNotFoundException':
                self._logger.info("Creating model: {}".format(model_name))
                self.client.create_model(
                    modelId=model_name,
                    modelType=model_type,
                    description=model_description,
                    eventTypeName=event_type_name,
                )
            else:
                raise error

        # Trigger training
        self._logger.info("Triggering training {}".format(model_name))
        response = self.client.create_model_version(
            modelId=model_name,
            modelType=model_type,
            trainingDataSource='EXTERNAL_EVENTS',
            trainingDataSchema={
                # Model Variables
                'modelVariables': model_features,
                # Label
                'labelSchema': {"labelMapper": model_label}
            },
            externalEventsDetail={
                'dataLocation': s3_training_file,
                'dataAccessRoleArn': role_arn
            }

        )
        model_version = response["modelVersionNumber"]
        self._logger.info("Training job kicked off for model {} version {}".format(model_name, model_version))

        # Wait for training to complete
        if wait:
            self.fraud_detector_utils.wait_until_model_status(model_name, model_version, model_type,
                                                              fail_states="ERROR", success_states="TRAINING_COMPLETE")

        response = self.client.get_model_version(modelId=model_name, modelType=model_type,
                                                 modelVersionNumber=model_version)

        return response
