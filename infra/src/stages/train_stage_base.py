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

from aws_cdk import core
from aws_cdk.aws_codebuild import BuildEnvironmentVariable
from aws_cdk.aws_codepipeline import Artifact
from aws_cdk.aws_codepipeline_actions import Action

StageActionList = List[Action]
OutputArtifacts = List[Artifact]
OutputVariables = Dict[str, BuildEnvironmentVariable]
VariableNamespace = str


class TrainStageBase:

    @property
    def name(self):
        return NotImplementedError

    @property
    def output_variables(self):
        return NotImplementedError

    def get_stage_actions(self, scope: core.Construct, env: str, stage_name: str,
                          source_artifacts: List[Artifact]) -> (StageActionList, VariableNamespace):
        """
        Creates  stage actions and returns the actions, the output artifacts and output variables
        :param env:
        :param scope:
        :param stage_name:
        :param source_artifacts:
        :return:
        """
        raise NotImplementedError
