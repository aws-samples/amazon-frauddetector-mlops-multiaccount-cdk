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
import logging
import time

import boto3
import botocore
from rules.detector_rule_base import DetectorRuleBase

FRAUD_DETECTOR_DATA_SOURCE_EVENT = 'EVENT'
FRAUD_DETECTOR_DATA_SOURCE_MODEL_SCORE = 'MODEL_SCORE'


class FraudDetectorUtils:

    def __init__(self, fraud_detector_client=None):
        self.fraud_detector_client = fraud_detector_client or boto3.client('frauddetector')

    @property
    def _logger(self):
        return logging.getLogger(__name__)

    def try_create_variable(self, variable_name, fraud_variable_type, data_type, default_value, description,
                            data_source=None):
        """
        Tries to create the variable if it doesnt already exist
        :param variable_name:
        :param fraud_variable_type:
        :param data_type:
        :param default_value:
        :param description:
        :param data_source:
        :return:
        """
        try:
            data_source = data_source or FRAUD_DETECTOR_DATA_SOURCE_EVENT
            variables_resp = self.fraud_detector_client.get_variables(name=variable_name)
            self._logger.info("Existing variable: {}".format(variable_name))

            assert len(variables_resp["variables"]) == 1, "Expecting just one variable"
            variable = variables_resp["variables"][0]

            # Verify that existing variables, potentially used by other models are not accidentally changed.
            # And raise an error if that is the case
            if variable["dataType"] != data_type \
                    or variable["dataSource"] != data_source \
                    or variable["variableType"] != fraud_variable_type \
                    or str(variable["defaultValue"]) != str(default_value):
                error_message_fmt = "The variable {} already exists, but the details {},{},{},{} do not match." \
                                    " Please change the variable name or delete the existing variable"
                raise ValueError(
                    error_message_fmt.format(json.dumps(variable), data_type, data_source, fraud_variable_type,
                                             default_value))

        except botocore.errorfactory.ClientError as error:
            # If resource not found, it means that the variable doesnt exist, so lets create it
            if error.response['Error']['Code'] == 'ResourceNotFoundException':
                self._logger.info("Creating variable: {}".format(variable_name))

                self.fraud_detector_client.create_variable(
                    name=variable_name,
                    dataType=data_type,
                    dataSource=data_source,
                    defaultValue=default_value,
                    description=description,
                    variableType=fraud_variable_type)
            else:
                raise error

        return variable_name

    def create_or_update_label(self, label, description):
        self._logger.info("Creating label {}".format(label))
        self.fraud_detector_client.put_label(name=label, description=description)
        return label

    def create_or_update_rule(self, detector_name: str, detector_rule: DetectorRuleBase):
        """

        :param detector_name: The name of the detector to attach the rule to
        :param detector_rule: An implementation of the detector rule base class
        :return:
        """

        rule_version = self._get_max_rule_version(detector_name, detector_rule.rule_id)

        if rule_version:
            rule_version = rule_version
            # Rule exists so update..
            self._logger.info("Rule id {} exists, updating ..".format(detector_rule.rule_id))

            resp = self.fraud_detector_client.update_rule_version(rule={"ruleId": detector_rule.rule_id,
                                                                        "detectorId": detector_name,
                                                                        "ruleVersion": str(int(rule_version))
                                                                        },
                                                                  description=detector_rule.description,
                                                                  expression=detector_rule.get_rule_expression(),
                                                                  language='DETECTORPL',
                                                                  outcomes=detector_rule.outcomes)

        else:
            # Rule doesnt exists
            self._logger.info("No rule found. Creating rule with id {}".format(detector_rule.rule_id))

            resp = self.fraud_detector_client.create_rule(
                ruleId=detector_rule.rule_id,
                detectorId=detector_name,
                description=detector_rule.description,
                expression=detector_rule.get_rule_expression(),
                language='DETECTORPL',
                outcomes=detector_rule.outcomes)

        rule_version = resp["rule"]["ruleVersion"]

        result = {
            "ruleId": detector_rule.rule_id,
            "detectorId": detector_name,
            "ruleVersion": str(rule_version)
        }

        return result

    def _get_max_rule_version(self, detector_name, rule_id):
        max_version = 0

        next_token = ""
        paginate = True

        while paginate:

            response = self.fraud_detector_client.get_rules(
                ruleId=rule_id,
                detectorId=detector_name,
                nextToken=next_token
            )

            # no rule with the given id found.
            if not response["ruleDetails"]:
                return None

            # Loop through the versions within the current page
            for rule in response["ruleDetails"]:
                version_no = float(rule["ruleVersion"])
                if version_no > max_version:
                    max_version = version_no

            next_token = response.get("nextToken", "")
            paginate = next_token != ""

        return max_version

    def wait_until_model_status(self, model_name, model_version, model_type, fail_states, success_states):
        """
        Polls for a model status until either it reaches the failure or success states
        :param model_name: Model name
        :param model_version: Model version
        :param model_type: Model type
        :param fail_states: a single state or a list of states indicating failure.
        :param success_states: a single state or a list of states indicating success.
        :return:
        """
        stime = time.time()
        job_inprogress = True

        # If single state string is passed , convert to list
        if isinstance(fail_states, str): fail_states = [fail_states]
        if isinstance(success_states, str): success_states = [success_states]

        end_states = fail_states + success_states

        while job_inprogress:
            response = self.fraud_detector_client.get_model_version(modelId=model_name, modelType=model_type,
                                                                    modelVersionNumber=str(model_version))

            reponse_status = response['status']
            if reponse_status not in end_states:
                self._logger.info(
                    "Current inprogress, state {}: {:.2f} minutes".format(reponse_status, (time.time() - stime) / 60))
                time.sleep(60)  # -- sleep for 60 seconds
            # Error
            elif reponse_status in fail_states:
                raise Exception("Failed to complete successfully {}".format(response))
            # Complete
            else:
                self._logger.info("Model status : " + reponse_status)
                job_inprogress = False
