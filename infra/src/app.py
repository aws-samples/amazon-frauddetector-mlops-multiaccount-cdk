#!/usr/bin/env python3

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
import os
from enum import Enum

from aws_cdk import core

from app_config_parser import AppConfigParser
from stacks.ci_pipeline_stack import CIPipelineStack
from stacks.data_stack import DataStack
from stacks.environment_bootstrap_stack import EnvironmentBootstrapStack
from stacks.fraud_detector_role_stack import FraudDetectorRoleStack
from stacks.machine_learning_pipeline_stack import MachineLearningPipelineStack


class StackType(str, Enum):
    EnvironmentBootstrap = "S1EnvironmentBootstrap"
    Data = "S2Data"
    MachineLearningPipeline = "S3MLPipeline"
    CIPipeline = "CIPipeline"
    FraudDetectorRole = "FraudDetectorRole"


def get_stack_name(stack_prefix: str, stack_type: StackType):
    return f"{stack_prefix}-{stack_type}"


def run(config_file):
    config_parser = AppConfigParser()
    stack_prefix, stack_design_dict = config_parser.parse_design(config_file)

    app = core.App()

    # Per Environment Stack
    EnvironmentBootstrapStack(app, "s1-environmentBootstrap",
                              stack_name=get_stack_name(stack_prefix, StackType.EnvironmentBootstrap))

    # Common Data stack
    DataStack(app, "s2-datastack", stack_name=get_stack_name(stack_prefix, StackType.Data))

    # Tools account ml pipeline stack
    args = stack_design_dict[StackType.MachineLearningPipeline]
    MachineLearningPipelineStack(app, "s3-mlpipelinestack",
                                 stack_name=get_stack_name(stack_prefix, StackType.MachineLearningPipeline), **args)

    # [Optional] Tools account ci pipeline stack
    args = stack_design_dict[StackType.CIPipeline]
    CIPipelineStack(app, "cipipelinestack", stack_name=get_stack_name(stack_prefix, StackType.CIPipeline), **args)

    # [Optional] FraudDetector role stack
    FraudDetectorRoleStack(app, "fdrolestack", stack_name=get_stack_name(stack_prefix, StackType.FraudDetectorRole))

    app.synth()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    default_config = os.path.join(os.path.dirname(__file__), "app_default_design_config.json")
    parser.add_argument("--configfile", help="Pass a config File", required=False, default=default_config)

    args = parser.parse_args()
    run(args.configfile)
