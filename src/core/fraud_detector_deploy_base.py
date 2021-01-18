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

from rules.detector_rule_base import DetectorRuleBase


class FraudDetectorDeployBase:
    """
    Base class for deploy
    """

    def deploy(self, detector_name: str, detector_description: str, event_type_name: str,
               detector_rules: DetectorRuleBase, rule_execution_mode: str = "FIRST_MATCHED",
               model_versions: list = None):
        """
        return a list of error messages if not valid. Return None if valid
        :param event_type:
        :param model_versions: A list of dict containing model information. For example: [{"modelId": model_name,
                                     "modelType": MODEL_TYPE_ONLINE_FRAUD_INSIGHTS,
                                     "modelDescription" : model_descriptions
                                     "modelVersionNumber": model_version}]
        :param detector_rules: A list of detector rules of type rule.detector_rule_base
        :param detector_description: Detector description
        :param detector_name: Detector name
        :param rule_execution_mode: Fraud detector rule execution mode, see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/frauddetector.html#FraudDetector.Client.create_detector_version
        :return:
        """
        raise NotImplementedError
