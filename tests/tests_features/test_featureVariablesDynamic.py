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

import pandas as pd
from features.feature_variables_dynamic import FeatureVariablesDynamic, FRAUD_DETECTOR_LABEL_KEY_FRAUD, \
    FRAUD_DETECTOR_LABEL_KEY_LEGIT


class TestFeatureVariablesDynamic(TestCase):

    def test_create_or_retrieve_features_email_field_name(self):
        # Arrange
        email_field_name = "customer_email"
        expected_var_type = "EMAIL_ADDRESS"
        expected_data_type = "STRING"
        default = ""
        desc = "Customer email address"

        field_descriptions_dict = {email_field_name: {"desc": desc}}

        input = [
            {email_field_name: "test@domain.com", "EVENT_LABEL": 0},
            {email_field_name: "test2@domain.com", "EVENT_LABEL": 1}

        ]

        df = pd.DataFrame(input)
        mock_fraud_detector_utils = MagicMock()

        sut = FeatureVariablesDynamic(df, true_labels=[1], fraud_detector_utils=mock_fraud_detector_utils,
                                      field_descriptions_dict=field_descriptions_dict)

        # Act
        sut.create_or_retrieve_features()

        # Assert
        mock_fraud_detector_utils.try_create_variable.assert_called_with(email_field_name, expected_var_type,
                                                                         expected_data_type, default, desc
                                                                         )

    def test_create_or_retrieve_features_email_field_value(self):
        # Arrange
        email_field_name = "customer_contact"
        expected_var_type = "EMAIL_ADDRESS"
        expected_data_type = "STRING"
        default = ""
        desc = "Customer email address"
        field_descriptions_dict = {email_field_name: {"desc": desc}}

        input = [
            {email_field_name: "test@domain.com", "EVENT_LABEL": 0},
            {email_field_name: "test2@domain.com", "EVENT_LABEL": 0}
        ]

        df = pd.DataFrame(input)
        mock_fraud_detector_utils = MagicMock()

        sut = FeatureVariablesDynamic(df, true_labels=[1], fraud_detector_utils=mock_fraud_detector_utils,
                                      field_descriptions_dict=field_descriptions_dict)

        # Act
        sut.create_or_retrieve_features()

        # Assert
        mock_fraud_detector_utils.try_create_variable.assert_called_with(email_field_name, expected_var_type,
                                                                         expected_data_type, default, desc
                                                                         )

    def test_create_or_retrieve_features_ip_field_value(self):
        # Arrange
        field_name = "customer_loc"
        expected_var_type = "IP_ADDRESS"
        expected_data_type = "STRING"
        default = ""
        desc = "Customer ip address"
        field_descriptions_dict = {field_name: {"desc": desc}}

        input = [
            {field_name: "123.22.22.11", "EVENT_LABEL": 0},
            {field_name: "124.22.22.11", "EVENT_LABEL": 0},
            {field_name: "124.22.22.0", "EVENT_LABEL": 1}
        ]

        df = pd.DataFrame(input)
        mock_fraud_detector_utils = MagicMock()

        sut = FeatureVariablesDynamic(df, true_labels=[1], fraud_detector_utils=mock_fraud_detector_utils,
                                      field_descriptions_dict=field_descriptions_dict)

        # Act
        sut.create_or_retrieve_features()

        # Assert
        mock_fraud_detector_utils.try_create_variable.assert_called_with(field_name, expected_var_type,
                                                                         expected_data_type, default, desc
                                                                         )

    def test_create_or_retrieve_features_custom_numeric(self):
        # Arrange
        field_name = "PaymentAmount"
        expected_var_type = "NUMERIC"
        expected_data_type = "FLOAT"
        default = 0.0
        desc = "Customer total amount"
        field_descriptions_dict = {field_name: {"desc": desc}}

        input = [
            {field_name: 23.0, "EVENT_LABEL": 0}
        ]

        df = pd.DataFrame(input)
        mock_fraud_detector_utils = MagicMock()

        sut = FeatureVariablesDynamic(df, true_labels=[1], fraud_detector_utils=mock_fraud_detector_utils,
                                      field_descriptions_dict=field_descriptions_dict)

        # Act
        sut.create_or_retrieve_features()

        # Assert
        mock_fraud_detector_utils.try_create_variable.assert_called_with(field_name, expected_var_type,
                                                                         expected_data_type, default, desc
                                                                         )

    def test_create_or_retrieve_features_custom_categorical(self):
        # Arrange
        field_name = "PaymentType"
        expected_var_type = "CATEGORICAL"
        expected_data_type = "STRING"
        default = ""
        desc = "Payment type"
        field_descriptions_dict = {field_name: {"desc": desc}}

        input = [
            {field_name: "CC", "EVENT_LABEL": 0},
            {field_name: "CASH", "EVENT_LABEL": 0},
            {field_name: "CASH", "EVENT_LABEL": 0},
            {field_name: "EFTPOS", "EVENT_LABEL": 1}
        ]

        df = pd.DataFrame(input)
        df[field_name] = df[field_name].astype('category')
        mock_fraud_detector_utils = MagicMock()

        sut = FeatureVariablesDynamic(df, true_labels=[1], fraud_detector_utils=mock_fraud_detector_utils,
                                      field_descriptions_dict=field_descriptions_dict)

        # Act
        sut.create_or_retrieve_features()

        # Assert
        mock_fraud_detector_utils.try_create_variable.assert_called_with(field_name, expected_var_type,
                                                                         expected_data_type, default, desc
                                                                         )

    def test_create_or_retrieve_features_custom_generic(self):
        # Arrange
        field_name = "PaymentDesc"
        expected_var_type = "FREE_FORM_TEXT"
        expected_data_type = "STRING"
        default = ""
        desc = "Payment description"
        field_descriptions_dict = {field_name: {"desc": desc}}

        input = [
            {field_name: "This is a return", "EVENT_LABEL": 0},
            {field_name: "This is a purchase", "EVENT_LABEL": 1}

        ]

        df = pd.DataFrame(input)
        mock_fraud_detector_utils = MagicMock()

        sut = FeatureVariablesDynamic(df, true_labels=[1], fraud_detector_utils=mock_fraud_detector_utils,
                                      field_descriptions_dict=field_descriptions_dict)

        # Act
        sut.create_or_retrieve_features()

        # Assert
        mock_fraud_detector_utils.try_create_variable.assert_called_with(field_name, expected_var_type,
                                                                         expected_data_type, default, desc
                                                                         )

    def test_create_or_retrieve_features_custom_override(self):
        # Arrange
        field_name = "PaymentDesc"
        expected_var_type = "CATEGORICAL"
        expected_data_type = "STRING"
        default = ""
        desc = "Payment description"
        field_descriptions_dict = {field_name: {"desc": desc, "variableType": "CATEGORICAL"}}

        input = [
            {field_name: "This is a return"},
            {field_name: "This is a purchase"}

        ]

        df = pd.DataFrame(input)
        mock_fraud_detector_utils = MagicMock()

        sut = FeatureVariablesDynamic(df, true_labels=[1], fraud_detector_utils=mock_fraud_detector_utils,
                                      field_descriptions_dict=field_descriptions_dict)

        # Act
        sut.create_or_retrieve_features()

        # Assert
        mock_fraud_detector_utils.try_create_variable.assert_called_with(field_name, expected_var_type,
                                                                         expected_data_type, default, desc
                                                                         )

    def test_create_or_retrieve_features_return_variable_names(self):
        # Arrange
        field_name_1 = "PaymentDesc"

        input = [
            {field_name_1: "This is a return"},
            {field_name_1: "This is a purchase"}

        ]

        df = pd.DataFrame(input)
        mock_fraud_detector_utils = MagicMock()

        sut = FeatureVariablesDynamic(df, true_labels=[1], fraud_detector_utils=mock_fraud_detector_utils)

        # Act
        actual = sut.create_or_retrieve_features()

        # Assert
        self.assertSequenceEqual([field_name_1], actual)

    def test_create_or_retrieve_labels(self):
        # Arrange
        field_descriptions_dict = None

        input = [
            {"Text": "This is a return", "EVENT_LABEL": 0},
            {"Text": "This is a purchase", "EVENT_LABEL": 1}

        ]
        expected = {FRAUD_DETECTOR_LABEL_KEY_FRAUD: ['1'],
                    FRAUD_DETECTOR_LABEL_KEY_LEGIT: ['0']}

        df = pd.DataFrame(input)
        mock_fraud_detector_utils = MagicMock()

        sut = FeatureVariablesDynamic(df, true_labels=[1], fraud_detector_utils=mock_fraud_detector_utils,
                                      field_descriptions_dict=field_descriptions_dict)

        # Act
        actual = sut.create_or_retrieve_label()

        # Assert
        mock_fraud_detector_utils.create_or_update_label.assert_called_with('0', "Legit flag")
        self.assertEqual(expected, actual)
