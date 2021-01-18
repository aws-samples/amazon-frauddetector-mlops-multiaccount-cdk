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

import re

from core.fraud_detector_utils import FraudDetectorUtils

FRAUD_DETECTOR_DATATYPE_STRING = 'STRING'

FRAUD_DETECTOR_DATATYPE_NUMERIC = "FLOAT"

FRAUD_DETECTOR_VARTYPE_EMAIL = "EMAIL_ADDRESS"

FRAUD_DETECTOR_VARTYPE_IP = "IP_ADDRESS"

FRAUD_DETECTOR_VARTYPE_CUSTOM_NUMERIC = "NUMERIC"

FRAUD_DETECTOR_VARTYPE_CUSTOM_CATEGORICAL = "CATEGORICAL"

FRAUD_DETECTOR_VARTYPE_CUSTOM_TEXT = "FREE_FORM_TEXT"

FRAUD_DETECTOR_LABEL_KEY_LEGIT = "LEGIT"

FRAUD_DETECTOR_LABEL_KEY_FRAUD = "FRAUD"

FRAUD_DETECTOR_LABEL_MAPPER = "labelMapper"


class FeatureVariablesDynamic:
    """
    Dynamically generated features from data
    """

    def __init__(self, df, true_labels, field_descriptions_dict=None, fraud_detector_utils=None):
        """
Dynamically detects the variable types
        :type true_labels: List
        :param df: Dataframe containing the input data
        :param field_descriptions_dict: A dictionary of field name to override default, desc and the fraud detector variable type
            {
                field_name: {"desc": desc,
                        "variableType":varType,
                        "default" :0.0}

            }
        :param fraud_detector_utils:
        """

        self.true_labels = true_labels
        self.field_descriptions_dict = field_descriptions_dict or {}
        self._fraud_detector_utils = fraud_detector_utils or FraudDetectorUtils()
        self.df = df
        self.var_type_dtype_map = {
            FRAUD_DETECTOR_VARTYPE_CUSTOM_TEXT: FRAUD_DETECTOR_DATATYPE_STRING,
            FRAUD_DETECTOR_VARTYPE_CUSTOM_NUMERIC: FRAUD_DETECTOR_DATATYPE_NUMERIC
        }

    def create_or_retrieve_features(self):
        """
        Creates & retrieves the variable names
        :return: a list of variable names to use for Fraud Detector. e.g. ["name", "address"]
        """

        prioritised_type_check_funcs = [
            self._is_email,
            self._is_ip,
            self._is_custom_numeric,
            self._is_custom_categorical
        ]

        feature_field_names = list(set(self.df.columns) - {"EVENT_LABEL", "EVENT_TIMESTAMP"})
        for field_name in feature_field_names:
            # Least priority default
            default_settings = self.field_descriptions_dict.get(field_name, {})
            variable_type = FRAUD_DETECTOR_VARTYPE_CUSTOM_TEXT
            df_col_dtype = self.df.dtypes[field_name]
            default = ""

            # Auto detector next preference
            for check in prioritised_type_check_funcs:
                type_tuple = check(field_name, self.df[field_name].iloc[0], df_col_dtype)
                if type_tuple:
                    variable_type, default = type_tuple
                    break

            # Override if values pass in setting dict
            default = default_settings.get("default", default)
            variable_type = default_settings.get("variableType", variable_type)
            data_type = self.var_type_dtype_map.get(variable_type, FRAUD_DETECTOR_DATATYPE_STRING)
            desc = default_settings.get("desc", field_name)

            self._fraud_detector_utils.try_create_variable(field_name, variable_type, data_type, default, desc)

        return feature_field_names

    def create_or_retrieve_label(self):
        """

        :return: Label variable name and a map of fraud vs legit flag. e.g {"LEGIT" :[0], "FRAUD" :[1] }

        """
        labels = self.df["EVENT_LABEL"].astype(str).unique()
        true_labels = [str(l) for l in self.true_labels]
        false_labels = list(set(labels) - set(true_labels))

        for l in true_labels:
            self._fraud_detector_utils.create_or_update_label(str(l), "Fraud flag")

        for l in false_labels:
            self._fraud_detector_utils.create_or_update_label(str(l), "Legit flag")

        label_schema = {FRAUD_DETECTOR_LABEL_KEY_FRAUD: true_labels,
                        FRAUD_DETECTOR_LABEL_KEY_LEGIT: false_labels}

        return label_schema

    def _is_email(self, field_name, field_value, dtype=None):

        if str(dtype) not in ['str', 'object']:
            return None

        result = (FRAUD_DETECTOR_VARTYPE_EMAIL, "")

        if "email" in field_name.lower():
            return result

        regex_email = r'^([a-z0-9._A-Z])+@(\w+\.\w+)+$'

        if re.search(regex_email, field_value.lower()):
            return result

        return None

    def _is_ip(self, field_name, field_value, dtype=None):
        if str(dtype) not in ['str', 'object']:
            return None

        result = (FRAUD_DETECTOR_VARTYPE_IP, "")

        if "ip_addr" in field_name.lower():
            return result

        regex_ip = r'^([0-9]{1,3}.){3}([0-9]{1,3}.)$'

        if re.search(regex_ip, field_value.lower()):
            return result

        return None

    def _is_custom_numeric(self, field_name, field_value, dtype=None):
        result = (FRAUD_DETECTOR_VARTYPE_CUSTOM_NUMERIC, 0.0)

        if str(dtype) in ["float64", "int64"]:
            return result

        return None

    def _is_custom_categorical(self, field_name, field_value, dtype=None):
        result = (FRAUD_DETECTOR_VARTYPE_CUSTOM_CATEGORICAL, "")
        if str(dtype) in ["category"]:
            return result

        return None
