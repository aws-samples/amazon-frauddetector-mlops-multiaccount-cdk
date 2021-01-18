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
from core.fraud_detector_deploy_base import FraudDetectorDeployBase
from core.fraud_detector_utils import FraudDetectorUtils

FRAUD_DETECTOR_RULE_MATCH_METHOD = "FIRST_MATCHED"

MODEL_TYPE_ONLINE_FRAUD_INSIGHTS = 'ONLINE_FRAUD_INSIGHTS'
DEPLOY_MODEL_STATUS = 'ACTIVE'


class FraudDetectorModelBasedDeploy(FraudDetectorDeployBase):
    """
    An implementation of a model based detector
    """

    def __init__(self, client=None, fraud_detector_utils=None):
        self.fraud_detector_utils = fraud_detector_utils or FraudDetectorUtils()
        self.client = client or boto3.client('frauddetector')

    @property
    def _logger(self):
        return logging.getLogger(__name__)

    def deploy(self, detector_name, detector_description, event_type_name: str, detector_rules,
               rule_execution_mode="FIRST_MATCHED", model_versions=None):
        """
        Deploy a model based Detector
        @param model_versions: A list of dict containing model information. For example: [{"modelId": model_name,
                                     "modelType": MODEL_TYPE_ONLINE_FRAUD_INSIGHTS,
                                     "modelDescription" : model_descriptions
                                     "modelVersionNumber": model_version}]
        @param detector_name:
        @param detector_rules:
        @param detector_description:
        @param rule_execution_mode: FIRST_MATCHED or ALL_MATCHED, see boto3 create_detector_version
        @return:
        """
        # Validate args
        assert model_versions is not None, "Model is mandatory"

        # Initialise detector
        self._logger.info("Initialise detector - {} ".format(detector_name))
        self.client.put_detector(
            detectorId=detector_name,
            eventTypeName=event_type_name,
            description=detector_description or detector_description)

        # Validate rules before hand..
        self._validate_rules(detector_rules)

        # Attempt to create the rule before deploying the model
        # So if rule creation fails, then the model doesnt run unnecessarily
        rules = []
        for r in detector_rules:
            for o in r.outcomes:
                self.client.put_outcome(name=o, description="Outcome for rule {}".format(r.description))
            rule_info = self.fraud_detector_utils.create_or_update_rule(detector_name, r)
            rules.append(rule_info)

        # Deploy  Models
        for model in model_versions:
            model_name = model['modelId']
            model_type = model['modelType']
            model_version = model['modelVersionNumber']
            self._logger.info("Deploying model {} with version {}".format(model_name, model_version))

            # Activate model
            self.client.update_model_version_status(
                modelId=model_name,
                modelType=model_type,
                modelVersionNumber=str(model_version),
                status=DEPLOY_MODEL_STATUS
            )
            # Wait for deployment to complete
            self.fraud_detector_utils.wait_until_model_status(model_name=model_name, model_version=model_version,
                                                              model_type=model_type, fail_states="ERROR",
                                                              success_states=DEPLOY_MODEL_STATUS)

            # Attach models and rules to detector
            self._logger.info("Assembling detector - {} with model {}".format(detector_name, model_name))

        # Copy all parameters except modelDescription to create detector version
        model_versions_p = [{k: v for k, v in i.items() if k != "modelDescription"} for i in model_versions]
        # Make sure model version is a string
        for v in model_versions_p:
            v["modelVersionNumber"] = str(v["modelVersionNumber"])

        response = self.client.create_detector_version(
            detectorId=detector_name,
            description=detector_description,
            modelVersions=model_versions_p,
            rules=rules,
            ruleExecutionMode=rule_execution_mode
        )
        detector_version = response["detectorVersionId"]

        # Activate detector
        self._logger.info(
            "Activate detector {}/{} ".format(detector_name, detector_version))
        self.client.update_detector_version_status(
            detectorId=detector_name,
            detectorVersionId=detector_version,
            status='ACTIVE'
        )

        self._logger.info("{} detector activated".format(detector_name))

        result = {
            "detectorVersionId": detector_version,
            "detectorId": detector_name
        }

        return result

    @staticmethod
    def _validate_rules(detector_rules=None):
        for r in detector_rules:
            error_messages = r.validate()
            if error_messages:
                raise ValueError("The rule {} is not valid due to {}".format(r.rule_id, error_messages))
