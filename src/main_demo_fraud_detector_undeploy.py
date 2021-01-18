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

from core.fraud_detector_undeploy import FraudDetectorUndeploy


def undeploy(model_name=None, model_version=None, detector_name=None):
    """
    UnDeploys a model with a single scoring rule based on model score
    :param model_name:
    :param model_version:
    :param detector_name:
    :return:
    """

    undeployer = FraudDetectorUndeploy()
    # Delete all detector versions

    if detector_name:
        undeployer.delete_detector(detector_name)

    if model_name is not None and model_version is not None:
        # Undeploy specific model version
        undeployer.undeploy_model(model_name, model_version)

    if detector_name is None and (model_name is None or model_version is None):
        raise ValueError(" Model name and model version must be specified or just the detector must be specified")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="The name of the model", required=False, default=None)
    parser.add_argument("--modelVersion", help="Version of the model", required=False, default=None)
    parser.add_argument("--detector", help="The name of the detector", required=False, default=None)

    parser.add_argument("--log-level", help="Log level", default="INFO", choices={"INFO", "WARN", "DEBUG", "ERROR"})
    args = parser.parse_args()
    print(args.__dict__)

    # Set up logging
    logging.basicConfig(level=logging.getLevelName(args.log_level), handlers=[logging.StreamHandler(sys.stdout)],
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Run
    undeploy(model_name=args.model, model_version=args.modelVersion, detector_name=args.detector)
