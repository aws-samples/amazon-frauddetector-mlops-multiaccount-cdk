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

import os
from typing import List

from aws_cdk import (
    core,
    aws_codepipeline_actions as actions,
    aws_iam as iam,
    aws_lambda,
    aws_codebuild, aws_codepipeline)
from aws_cdk.aws_codepipeline import Artifact
from aws_cdk.core import CfnParameter, Stack
from stages.train_stage_base import TrainStageBase, StageActionList, VariableNamespace

PROCESSED_DATAURI = "PROCESSED_DATAURI"

MODEL_URI = "MODEL_URI"

TRAINING_JOB_VERSION = "TRAINING_JOB_VERSION"

TRAINING_JOB_TYPE = "TRAINING_JOB_TYPE"

TRAINING_JOB_NAME = "TRAINING_JOB_NAME"


class TrainStageCodeBuildLongPolling(TrainStageBase):
    """
    Train code build. Expects the code build job to kick off a training job and output the
    """

    def __init__(self):
        self._obj = None

    def get_stage_actions(self, scope: core.Construct, env: str, stage_name: str,
                          source_artifacts: List[Artifact]) -> (StageActionList, VariableNamespace):
        self._set_common_params(scope)

        role, service_role = self.environment_specific_params(scope, env, stage_name)
        data_uri = self._cfn_data_uri_file_parameter.value_as_string

        code_build_variables_namespace = "{}{}Variables".format(env, stage_name)

        # Provide standard environment variables
        # Most tasks will need role to switch to, the data uri and the service role
        train_env_variables = {"SERVICE_ROLE_TO_ASSUME": aws_codebuild.BuildEnvironmentVariable(value=service_role,
                                                                                                type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT),
                               "DATA_URI": aws_codebuild.BuildEnvironmentVariable(value=data_uri,
                                                                                  type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT),
                               "ROLE_TO_ASSUME": aws_codebuild.BuildEnvironmentVariable(value=role,
                                                                                        type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT)}
        # Provide standard environment variables
        # Most tasks will need role to switch to, the data uri and the service role
        build_project = self._code_build

        # Provide switch role
        assume_role_statement = iam.PolicyStatement(actions=["sts:AssumeRole"], resources=[role])
        build_project.add_to_role_policy(assume_role_statement)

        build_artifact = aws_codepipeline.Artifact("{}{}Artifacts".format(env, stage_name))

        # Polling
        handler = self._handler
        handler.add_to_role_policy(assume_role_statement)

        codebuild_action = actions.CodeBuildAction(outputs=[build_artifact],
                                                   action_name=f"{env}{stage_name}",
                                                   project=build_project,
                                                   input=source_artifacts[0],
                                                   type=actions.CodeBuildActionType.BUILD,
                                                   run_order=1,
                                                   # role=build_project.role,
                                                   variables_namespace=code_build_variables_namespace,
                                                   environment_variables=train_env_variables)

        lambda_action = actions.LambdaInvokeAction(
            action_name="PollStatus{}".format(stage_name),
            lambda_=handler,
            run_order=2,
            user_parameters={
                "training_job_name": "#{{{}.{}}}".format(code_build_variables_namespace, TRAINING_JOB_NAME),
                "training_job_version": "#{{{}.{}}}".format(
                    code_build_variables_namespace, TRAINING_JOB_VERSION),
                "training_type": "#{{{}.{}}}".format(code_build_variables_namespace, TRAINING_JOB_TYPE),
                "assume_role": role
            }

        )

        return [codebuild_action, lambda_action], code_build_variables_namespace

    def environment_specific_params(self, scope: core.Construct, env: str, stage: str):
        stack_scope = Stack.of(scope)

        # service role
        service_role_parameter = CfnParameter(stack_scope, f"{env}{stage}ServiceRole", type="String",
                                              description="The role arn to use for the by the service",
                                              default="")
        service_role = service_role_parameter.value_as_string

        # Code build role
        role_parameter = CfnParameter(stack_scope, f"{env}{stage}ToolsCodeBuildRole", type="String",
                                      description="The role arn to use for the codebuild job")
        role = role_parameter.value_as_string

        return role, service_role

    @property
    def output_variables(self):
        """
        Expects the variables PROCESSED_DATAURI, MODEL_URI, TRAINING_JOB_VERSION, TRAINING_JOB_TYPE & TRAINING_JOB_NAME to be exported by the codebuild job
        :return: The names of the output variables
        """
        return [
            TRAINING_JOB_NAME, TRAINING_JOB_TYPE, TRAINING_JOB_VERSION, MODEL_URI, PROCESSED_DATAURI
        ]

    @property
    def variable_namespace(self):
        return NotImplementedError

    def _set_common_params(self, scope):
        if self._obj is not None: return
        self._obj = object()

        stage = "Train"

        stack_scope = Stack.of(scope)

        self._cfn_data_uri_file_parameter = CfnParameter(stack_scope, f"{stage}Datauri", type="String",
                                                         description="The data uri",
                                                         default="")

        self._cfn_buildspec_file_parameter = CfnParameter(stack_scope,
                                                          f"{stage}Buildspec",
                                                          type="String",
                                                          description="The name of the codebuild spec file. e.g. codebuild/buildspec.yml")

        self._cfn_build_image_parameter = CfnParameter(stack_scope, f"{stage}BuildImage", type="String",
                                                       description="The codebuild image as specified in https://docs.aws.amazon.com/codebuild/latest/userguide/codebuild-env-ref-available.html. e.g. aws/codebuild/amazonlinux2-x86_64-standard:2.0",
                                                       default="aws/codebuild/standard:4.0")

        # Lambda
        lambda_assets = os.path.join(os.path.dirname(__file__), "..", "lambda_poller")

        self._handler = aws_lambda.Function(scope, f"{stage}StatusHandler",
                                            runtime=aws_lambda.Runtime.PYTHON_3_8,
                                            code=aws_lambda.Code.asset(lambda_assets),
                                            handler="lambda_function.lambda_handler"
                                            )

        build_image = self._cfn_build_image_parameter.value_as_string
        buildspec_file = self._cfn_buildspec_file_parameter.value_as_string

        self._code_build = aws_codebuild.PipelineProject(
            scope,
            "{}CodeBuild".format(stage),
            environment=aws_codebuild.BuildEnvironment(
                build_image=aws_codebuild.LinuxBuildImage.from_code_build_image_id(build_image),
                privileged=True),
            build_spec=aws_codebuild.BuildSpec.from_source_filename(buildspec_file)
        )
