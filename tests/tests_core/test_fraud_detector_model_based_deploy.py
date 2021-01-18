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

from core.fraud_detector_model_based_deploy import FraudDetectorModelBasedDeploy, MODEL_TYPE_ONLINE_FRAUD_INSIGHTS


class TestFraudDetectorModelBasedDeploy(TestCase):

    def test_deploy_invalid_model_none(self):
        """
        Test case to validate that model none is not accepted
        :return:
        """
        # Arrange
        detector_name = "demo_detector"
        desc = "This is demo"
        model_versions = None

        mock_client = MagicMock()
        mock_utils = MagicMock()

        mock_detector_rule = MagicMock()
        mock_detector_rule.validate.return_value = None
        detector_rules = [mock_detector_rule]

        sut = FraudDetectorModelBasedDeploy(client=mock_client, fraud_detector_utils=mock_utils)

        # Act + assert
        with self.assertRaises(AssertionError) as _:
            sut.deploy(detector_name=detector_name, detector_description=desc, event_type_name=None,
                       detector_rules=detector_rules, model_versions=model_versions)

    def test_deploy_pass_through(self):
        """
        Test case  simply check if execution complete with no errors
        :return:
        """
        # Arrange
        detector_version = "2.0"
        detector_name = "demo_detector"
        desc = "This is demo"
        model_versions = [{"modelId": "demo_model",
                           "modelDescription": "This is a sample model",
                           "modelType": MODEL_TYPE_ONLINE_FRAUD_INSIGHTS,
                           "modelVersionNumber": "1.0"}]

        # Mock FD client
        mock_client = MagicMock()
        mock_client.create_detector_version.return_value = {
            "detectorVersionId": detector_version
        }

        # Mock utils
        mock_utils = MagicMock()

        # Mock rule
        mock_detector_rule = MagicMock()
        mock_detector_rule.validate.return_value = None
        detector_rules = [mock_detector_rule]

        sut = FraudDetectorModelBasedDeploy(client=mock_client, fraud_detector_utils=mock_utils)

        # Expected
        expected = {
            "detectorVersionId": detector_version,
            "detectorId": detector_name
        }

        # Act
        actual = sut.deploy(detector_name=detector_name, detector_description=desc, event_type_name=None,
                            detector_rules=detector_rules, model_versions=model_versions)

        # Assert
        self.assertEqual(expected, actual)
