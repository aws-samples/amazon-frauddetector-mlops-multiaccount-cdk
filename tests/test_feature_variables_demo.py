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

from feature_variables_demo import FeatureVariablesDemo


class TestFeatureVariablesSimple(TestCase):

    def test_create_or_retrieve_features(self):
        """
        Test the variables are returned
        :return:
        """
        # Arrange
        mock_fraud_detector_utils = MagicMock()
        sut = FeatureVariablesDemo(fraud_detector_utils=mock_fraud_detector_utils)
        expected_num_variables = 2

        # Act
        actual_variables = sut.create_or_retrieve_features()

        # Assert
        self.assertEqual(len(actual_variables), expected_num_variables)
