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

import argparse
import logging
import sys

import pandas as pd
from features.feature_variables_dynamic import FeatureVariablesDynamic

from core.fraud_detector_event import FraudDetectorEvent
from core.fraud_detector_train import FraudDetectorTrain

MODEL_TYPE_ONLINE_FRAUD_INSIGHTS = 'ONLINE_FRAUD_INSIGHTS'

EVENT_TYPE_NAME = "demoevent"


def train(model_name, s3uri, sample_data, wait, role):
    """
    Runs a demo training job using simple mandatory features
    :param sample_data:
    :param model_name:
    :param s3uri:
    :param wait:
    :param role:
    :return:
    """
    model_variables = FeatureVariablesDynamic(df=pd.read_csv(sample_data), true_labels=[1])
    model_event = FraudDetectorEvent()
    trainer = FraudDetectorTrain()

    # Create event
    model_event.create_event(event_type_name=EVENT_TYPE_NAME, description="This is a demo event", entity="democustomer",
                             model_variables=model_variables)
    # Create model
    model_details = trainer.run(model_name=model_name, model_variables=model_variables,
                                model_description="This is a demo model", model_type=MODEL_TYPE_ONLINE_FRAUD_INSIGHTS,
                                s3_training_file=s3uri, role_arn=role, wait=wait, event_type_name=EVENT_TYPE_NAME)

    ## NOTE: Important, so build can use regex to pick up the model version
    print("##ModelVersion##:{}".format(model_details["modelVersionNumber"]))
    print("##ModelName##:{}".format(model_details["modelId"]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--s3uri", help="The s3 training data file url", required=True)
    parser.add_argument("--sampledata",
                        help="A subset of training data used to dynamically create variables in fraud detector",
                        required=True)
    parser.add_argument("--model", help="The name of the model", required=False, default="demo_model")

    parser.add_argument("--role", help="The role arn to be used by Fraud detector to access s3 data", required=True)
    parser.add_argument("--wait",
                        help="""Waits until the training job completes. 
                        When false triggers the training job and exists immediately without waiting for it to complete.. """,
                        required=False,
                        default=0, type=int, choices={0, 1})

    parser.add_argument("--log-level", help="Log level", default="INFO", choices={"INFO", "WARN", "DEBUG", "ERROR"})
    args = parser.parse_args()
    print(args.__dict__)

    # Set up logging
    logging.basicConfig(level=logging.getLevelName(args.log_level), handlers=[logging.StreamHandler(sys.stdout)],
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Run
    train(role=args.role, model_name=args.model, wait=args.wait, s3uri=args.s3uri, sample_data=args.sampledata)
