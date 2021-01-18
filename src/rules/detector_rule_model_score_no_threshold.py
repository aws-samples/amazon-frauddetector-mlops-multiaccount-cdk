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

from core.fraud_detector_utils import FraudDetectorUtils, FRAUD_DETECTOR_DATA_SOURCE_MODEL_SCORE
from rules.detector_rule_base import DetectorRuleBase


class DetectorRuleModelScoreNoThreshold(DetectorRuleBase):

    def validate(self):
        """
        This is use if no thresholding is required
        :return:
        """
        return None

    def __init__(self, rule_id, model_name, fraud_detector_utils=None):
        self.fraud_detector_utils = fraud_detector_utils or FraudDetectorUtils()
        self.model_name = model_name
        self._rule_id = rule_id

    @property
    def rule_id(self):
        return self._rule_id

    @property
    def outcomes(self):
        return ["outcome_no_threshold"]

    @property
    def description(self):
        return "Returns  outcome if the model score is greater than threshold"

    def get_rule_expression(self):
        """
        Returns a single rule expression
        :return:
        """
        # TODO: check doesnt look like model score variable can be changed.
        model_score_variable = "{}_insightscore".format(self.model_name)

        # Create variable if it doesnt exists
        self.fraud_detector_utils.try_create_variable(model_score_variable, data_type="FLOAT", default_value="0.0",
                                                      data_source=FRAUD_DETECTOR_DATA_SOURCE_MODEL_SCORE,
                                                      fraud_variable_type="NUMERIC", description="Model score variable")

        rule_expression = f"${model_score_variable} >= 0"

        return rule_expression
