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

from unittest import TestCase
from unittest.mock import MagicMock

import botocore
from core.fraud_detector_utils import FraudDetectorUtils


class TestFraudDetectorUtils(TestCase):

    def test_get_features_variables_exist(self):
        """
        The variables already exist in Fraud detector
        :return:
        """
        # Arrange
        expected_num_variable = "dummy"
        data_type = "float"
        default = 0.0
        fraud_variable_type = "IP_ADDRESS"

        mock_fraud_detector = MagicMock()
        mock_fraud_detector.get_variables.return_value = {
            'variables': [
                {
                    'name': expected_num_variable,
                    'dataType': data_type,
                    'dataSource': 'EVENT',
                    'defaultValue': default,
                    'description': 'Dummy variable',
                    'variableType': fraud_variable_type,
                    'lastUpdatedTime': '2019-01-02',
                    'createdTime': '2019-01-01'
                },
            ],
            'nextToken': ''
        }
        sut = FraudDetectorUtils(fraud_detector_client=mock_fraud_detector)

        # Act

        actual_variable_name = sut.try_create_variable(data_type=data_type, default_value=default, description="mock",
                                                       variable_name=expected_num_variable,
                                                       fraud_variable_type=fraud_variable_type)

        # Assert
        self.assertEqual(expected_num_variable, actual_variable_name)

    def test_get_features_create_variables(self):
        """
        The variables do not exist and need to be created
        :return:
        """
        # Arrange
        expected_num_variable = "dummy"
        mock_fraud_detector = MagicMock()
        mock_fraud_detector.get_variables.side_effect = botocore.errorfactory.ClientError(
            error_response={"Error": {"Code": "ResourceNotFoundException"}}, operation_name="GetVariables")
        sut = FraudDetectorUtils(fraud_detector_client=mock_fraud_detector)

        # Act
        actual_variable_name = sut.try_create_variable(data_type="float", default_value=0.0, description="mock",
                                                       variable_name=expected_num_variable,
                                                       fraud_variable_type="IP_ADDRESS")

        # Assert
        mock_fraud_detector.create_variable.assert_called()
        self.assertEqual(expected_num_variable, actual_variable_name)
