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

from typing import List, Dict

from aws_cdk import (
    core
)
from custom_constructs.ml_pipeline_construct import MLPipelineConstruct


class MachineLearningPipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, *, repo_type: str, train_stage_type: str,
                 deploy_stage_type: str = None, environments: List[Dict[str, str]] = None, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        MLPipelineConstruct(self, id="FDPipeline", repo_type=repo_type, train_stage_type=train_stage_type,
                            deploy_stage_type=deploy_stage_type, envs=environments)
