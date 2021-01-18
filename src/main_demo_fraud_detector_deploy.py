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

from core.fraud_detector_model_based_deploy import FraudDetectorModelBasedDeploy, FRAUD_DETECTOR_RULE_MATCH_METHOD
from main_demo_fraud_detector_train import EVENT_TYPE_NAME
from rules.detector_rule_model_score_positive import DetectorRuleModelScorePositive

MODEL_TYPE_ONLINE_FRAUD_INSIGHTS = 'ONLINE_FRAUD_INSIGHTS'


def deploy(model_name, model_version, detector_name, detector_description, model_description, event_name):
    """
    Deploys a model with a single scoring rule based on model score
    :param event_name: Event name
    :param model_description: Model description
    :param detector_description: Detector description
    :param model_name: Model name
    :param model_version: Model version, e.g. 1.0
    :param detector_name: Detector name
    :return:
    """
    detector_rules = [
        DetectorRuleModelScorePositive(rule_id="positivescorerule", model_name=model_name, threshold=950)
    ]
    deployer = FraudDetectorModelBasedDeploy()

    deployer.deploy(detector_name=detector_name, detector_description=detector_description, event_type_name=event_name,
                    detector_rules=detector_rules, rule_execution_mode=FRAUD_DETECTOR_RULE_MATCH_METHOD,
                    model_versions=[{"modelId": model_name,
                                     "modelDescription": model_description,
                                     "modelType": MODEL_TYPE_ONLINE_FRAUD_INSIGHTS,
                                     "modelVersionNumber": model_version}])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="The name of the model", required=True)
    parser.add_argument("--event", help="The name of the event", required=False, default=EVENT_TYPE_NAME)
    parser.add_argument("--modelVersion", help="Version of the model", required=True, type=float)
    parser.add_argument("--modelDesc", help="Model version description", required=False, default="Demo sample")
    parser.add_argument("--detector", help="The name of the detector", required=True)
    parser.add_argument("--detectorDesc", help="Detector description", required=False, default="Demo sample")

    parser.add_argument("--log-level", help="Log level", default="INFO", choices={"INFO", "WARN", "DEBUG", "ERROR"})
    args = parser.parse_args()
    print(args.__dict__)

    # Set up logging
    logging.basicConfig(level=logging.getLevelName(args.log_level), handlers=[logging.StreamHandler(sys.stdout)],
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Run
    deploy(model_name=args.model, model_version=args.modelVersion, detector_name=args.detector,
           detector_description=args.detectorDesc, model_description=args.modelDesc, event_name=args.event)
