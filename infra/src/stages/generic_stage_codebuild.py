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

from typing import List

from aws_cdk import (
    core,
    aws_codepipeline_actions as actions,
    aws_codebuild, aws_codepipeline)
from aws_cdk.aws_codepipeline import Artifact
from stages.train_stage_base import StageActionList, VariableNamespace

PROCESSED_DATAURI = "PROCESSED_DATAURI"

MODEL_URI = "MODEL_URI"

TRAINING_JOB_VERSION = "TRAINING_JOB_VERSION"

TRAINING_JOB_TYPE = "TRAINING_JOB_TYPE"

TRAINING_JOB_NAME = "TRAINING_JOB_NAME"


class GenericStageCodeBuild:
    """
    Train code build. Expects the code build job to kick off a training job and output the
    """

    def get_stage_actions(self, scope: core.Construct, stage_name: str,
                          source_artifacts: List[Artifact], buildspec_file, build_image) -> (
            StageActionList, VariableNamespace):
        code_build_project = aws_codebuild.PipelineProject(
            scope,
            "{}CodeBuild".format(stage_name),
            environment=aws_codebuild.BuildEnvironment(
                build_image=aws_codebuild.LinuxBuildImage.from_code_build_image_id(
                    build_image),
                privileged=True),
            build_spec=aws_codebuild.BuildSpec.from_source_filename(buildspec_file)
        )

        code_build_variables_namespace = "{}Variables".format(stage_name)

        build_artifact = aws_codepipeline.Artifact("{}Artifacts".format(stage_name))

        codebuild_action = actions.CodeBuildAction(outputs=[build_artifact],
                                                   action_name=f"{stage_name}",
                                                   project=code_build_project,
                                                   input=source_artifacts[0],
                                                   type=actions.CodeBuildActionType.BUILD,
                                                   run_order=1,
                                                   # role=build_project.role,
                                                   variables_namespace=code_build_variables_namespace)

        return [codebuild_action], code_build_variables_namespace
