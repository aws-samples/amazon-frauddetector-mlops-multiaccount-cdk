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
from core.fraud_detector_utils import FraudDetectorUtils


class FraudDetectorUndeploy:

    def __init__(self, client=None, fraud_detector_utils=None):
        self.client = client or boto3.client('frauddetector')
        self.fraud_detector_utils = fraud_detector_utils or FraudDetectorUtils()

    @property
    def _logger(self):
        return logging.getLogger(__name__)

    def delete_detector(self, detector_name):

        self.delete_all_detector_versions(detector_name)

        # delete rules attached to detector
        self.delete_all_rules(detector_name)

        self.client.delete_detector(
            detectorId=detector_name
        )

    def delete_all_rules(self, detector_name):
        next_token = ""
        paginate = True
        while paginate:

            response = self.client.get_rules(
                detectorId=detector_name,
                nextToken=next_token
            )

            # no rule with the given id found.
            if not response["ruleDetails"]:
                break

            # Loop through the versions within the current page
            for rule in response["ruleDetails"]:
                rule_id = rule["ruleId"]
                rule_version = rule["ruleVersion"]
                # delete detector version rules
                response = self.client.delete_rule(
                    rule={"detectorId": detector_name,
                          "ruleId": rule_id,
                          "ruleVersion": str(rule_version)
                          }
                )

            next_token = response.get("nextToken", "")
            paginate = next_token != ""

    def delete_all_detector_versions(self, detector_name):
        # get detector versions:
        next_token = ""
        paginate = True
        while paginate:

            response = self.client.describe_detector(
                detectorId=detector_name,
                nextToken=next_token
            )

            # no versions found.
            if not response["detectorVersionSummaries"]:
                break

            # Loop through the versions within the current page
            for detector_version in response["detectorVersionSummaries"]:
                version_no = detector_version["detectorVersionId"]

                self.client.update_detector_version_status(
                    detectorId=detector_name,
                    detectorVersionId=str(version_no),
                    status='INACTIVE'
                )

                # delete detector version
                response = self.client.delete_detector_version(
                    detectorId=detector_name,
                    detectorVersionId=str(version_no)
                )

            next_token = response.get("nextToken", "")
            paginate = next_token != ""

    def undeploy_model(self, model_name, model_version, model_type='ONLINE_FRAUD_INSIGHTS'):
        self.client.update_model_version_status(
            modelId=model_name,
            modelType=model_type,
            modelVersionNumber=model_version,
            status='INACTIVE'
        )
        self.fraud_detector_utils.wait_until_model_status(model_name=model_name, model_version=model_version,
                                                          model_type=model_type, fail_states="ERROR",
                                                          success_states="TRAINING_COMPLETE")
