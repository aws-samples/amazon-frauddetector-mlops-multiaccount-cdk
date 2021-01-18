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

from core.fraud_detector_train import FraudDetectorTrain


class TestFraudDetectorTrain(TestCase):

    def setUp(self):
        self.model_name = 'demo_model'
        self.model_description = 'This is demo'
        self.model_type = 'ONLINE_FRAUD_INSIGHTS'
        self.s3_training_file = 's3://mybucket/demo.csv'
        self.role_arn = ' arn:aws:iam::11111:role/fraudetectordataaccessrole'
        self.model_version = '1.0'
        self.final_response = {
            "status": "TRAINING_COMPLETE"
        }

    def test_run_without_wait(self):
        """
        Test the internal function calls received with the given params
        :return:
        """
        # Arrange
        mock_model_variables = MagicMock()
        mock_fraud_detector = MagicMock()
        mock_utils = MagicMock()

        mock_fraud_detector.create_model_version.return_value = {
            'modelVersionNumber': self.model_version
        }

        mock_fraud_detector.get_model_version.return_value = self.final_response

        sut = FraudDetectorTrain(client=mock_fraud_detector, fraud_detector_utils=mock_utils)

        # Act
        actual = sut.run(model_name=self.model_name, model_variables=mock_model_variables,
                         model_description=self.model_description, model_type=self.model_type,
                         s3_training_file=self.s3_training_file, role_arn=self.role_arn, event_type_name="demo")

        # Assert
        self.assertEqual(self.final_response, actual)
        mock_utils.wait_until_model_status.assert_not_called()

    def test_run_with_wait(self):
        """
        Test the internal function calls receive the given params
        :return:
        """
        # Arrange

        mock_model_variables = MagicMock()
        mock_fraud_detector = MagicMock()
        mock_utils = MagicMock()

        mock_fraud_detector.create_model_version.return_value = {
            'modelVersionNumber': self.model_version
        }

        sut = FraudDetectorTrain(client=mock_fraud_detector, fraud_detector_utils=mock_utils)

        # Act
        sut.run(model_name=self.model_name, model_variables=mock_model_variables,
                model_description=self.model_description, model_type=self.model_type,
                s3_training_file=self.s3_training_file, role_arn=self.role_arn, wait=True, event_type_name="demo")

        # Assert
        mock_utils.wait_until_model_status.assert_called_with(self.model_name, self.model_version, self.model_type,
                                                              fail_states='ERROR', success_states='TRAINING_COMPLETE')
