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

import boto3
from features.feature_variables_base import FeatureVariablesBase

FRAUD_DETECTOR_LABEL_KEY_LEGIT = "LEGIT"

FRAUD_DETECTOR_LABEL_KEY_FRAUD = "FRAUD"


class FraudDetectorEvent:
    """
    Creates a fraud detector event
    """

    def __init__(self, client=None):
        self.client = client or boto3.client('frauddetector')

    @property
    def _logger(self):
        return logging.getLogger(__name__)

    def create_event(self, event_type_name: str, model_variables: FeatureVariablesBase, entity: str, description: str,
                     entity_description: str = None):
        # Create model features
        model_features = model_variables.create_or_retrieve_features()
        # Create labels
        model_label_map = model_variables.create_or_retrieve_label()
        model_labels = model_label_map[FRAUD_DETECTOR_LABEL_KEY_LEGIT] + model_label_map[FRAUD_DETECTOR_LABEL_KEY_FRAUD]

        # Create entity type
        self.client.put_entity_type(
            name=entity,
            description=entity_description or description
        )

        # Create event type
        self.client.put_event_type(
            name=event_type_name,
            description=description,
            eventVariables=model_features,
            labels=model_labels,
            entityTypes=[entity]
        )
