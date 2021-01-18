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

from features.feature_variables_base import FeatureVariablesBase

from core.fraud_detector_utils import FraudDetectorUtils

FRAUD_DETECTOR_LABEL_KEY_LEGIT = "LEGIT"

FRAUD_DETECTOR_LABEL_KEY_FRAUD = "FRAUD"

FRAUD_DETECTOR_LABEL_MAPPER = "labelMapper"

FRAUD_DETECTOR_FIELD_TYPE_LABEL = 'labelKey'

FRAUD_DETECTOR_DATATYPE_STRING = 'STRING'

FRAUD_DETECTOR_FIELDTYPE_EMAIL = "EMAIL_ADDRESS"

FRAUD_DETECTOR_FIELDTYPE_IP = "IP_ADDRESS"

FRAUD_DETECTOR_FIELDTYPE_TIMESTAMP = "EVENT_TIMESTAMP"


class FeatureVariablesDemo(FeatureVariablesBase):
    """
    This is a simple variable set where only the required features for Amazon feature set are set up
    """

    def __init__(self, fraud_detector_utils=None):
        self._fraud_detector_utils = fraud_detector_utils or FraudDetectorUtils()

    @property
    def fraud_detector_utils(self):
        return self._fraud_detector_utils

    def create_or_retrieve_features(self):
        """
        Creates the variables and returns the names
        """
        for k, v in self._feature_details.items():
            self.fraud_detector_utils.try_create_variable(k, v["variableType"], v["dataType"], v["default"], v["desc"])

        result = list(self._feature_details.keys())
        return result

    def create_or_retrieve_label(self):
        """
        Return the label field and mappings as required by fraud detector
        :return:
        """
        self.fraud_detector_utils.create_or_update_label("1", "Fraud flag")
        self.fraud_detector_utils.create_or_update_label("0", "Legit flag")

        label_schema = {FRAUD_DETECTOR_LABEL_KEY_FRAUD: ["1"],
                        FRAUD_DETECTOR_LABEL_KEY_LEGIT: ["0"]}

        return label_schema

    @property
    def _feature_details(self):
        feature_details = {

            "email": {"variableType": FRAUD_DETECTOR_FIELDTYPE_EMAIL,
                      "desc": "Email address",
                      "default": "",
                      "dataType": FRAUD_DETECTOR_DATATYPE_STRING},

            "ip": {"variableType": FRAUD_DETECTOR_FIELDTYPE_IP,
                   "desc": "IP address",
                   "default": "",
                   "dataType": FRAUD_DETECTOR_DATATYPE_STRING}
        }
        return feature_details

    @property
    def _logger(self):
        return logging.getLogger(__name__)
