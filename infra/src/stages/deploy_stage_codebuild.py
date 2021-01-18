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
    aws_iam,
    aws_codebuild, aws_codepipeline)
from aws_cdk.aws_codepipeline import Artifact
from aws_cdk.core import CfnParameter, Stack
from stages.deploy_stage_base import DeployStageBase, StageActionList, VariableNamespace


class DeployStageCodeBuild(DeployStageBase):

    def __init__(self):
        self._obj = None

    @property
    def name(self):
        return "DeployCodeBuild"

    @property
    def output_variables(self):
        return []

    def get_stage_actions(self, scope: core.Construct, env: str, stage_name: str, source_artifacts: List[Artifact],
                          train_job_output_variables: List[str], train_job_namespace: VariableNamespace) -> (
            StageActionList, VariableNamespace):
        service_role, role = self._environment_specific_params(scope, env, stage_name)
        self._set_common_params(scope)

        env_variables = {}
        for v in train_job_output_variables:
            env_variables[v] = aws_codebuild.BuildEnvironmentVariable(value="#{{{}.{}}}".format(train_job_namespace, v),
                                                                      type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT)

        env_variables["ROLE_TO_ASSUME"] = aws_codebuild.BuildEnvironmentVariable(value=role,
                                                                                 type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT)

        stage_variable_namespace = "{}{}Variable".format(env, stage_name)

        build_project = self._code_build

        # Provide switch role
        assume_role_statement = aws_iam.PolicyStatement(actions=["sts:AssumeRole"], resources=[role])
        build_project.add_to_role_policy(assume_role_statement)

        build_artifact = aws_codepipeline.Artifact("{}{}Artifacts".format(env, stage_name))

        # Include output from the training job as input to the deploy

        codebuild_action = actions.CodeBuildAction(outputs=[build_artifact],
                                                   action_name=f"{env}{stage_name}",
                                                   project=build_project,
                                                   input=source_artifacts[0],
                                                   type=actions.CodeBuildActionType.BUILD,
                                                   run_order=1,
                                                   # role=build_project.role,
                                                   variables_namespace=stage_variable_namespace,
                                                   environment_variables=env_variables)

        return [codebuild_action], stage_variable_namespace

    def _environment_specific_params(self, scope: core.Construct, env: str, stage: str):

        stack_scope = Stack.of(scope)
        # service role
        service_role_parameter = CfnParameter(stack_scope, f"{env}{stage}ServiceRole", type="String",
                                              description="The role arn to use for the by the service",
                                              default="")
        service_role = service_role_parameter.value_as_string

        role_parameter = CfnParameter(stack_scope, f"{env}{stage}ToolsCodeBuildRole", type="String",
                                      description="[Optional] The role arn to use for the codebuild job")
        role = role_parameter.value_as_string

        return service_role, role

    def _set_common_params(self, scope):
        if self._obj is None:
            self._obj = object()
            stage = "Deploy"

            stack_scope = Stack.of(scope)

            self._cfn_buildspec_file_parameter = CfnParameter(stack_scope,
                                                              f"{stage}Buildspec",
                                                              type="String",
                                                              description="The name of the codebuild spec file. e.g. codebuild/buildspec.yml")

            self._cfn_build_image_parameter = CfnParameter(stack_scope, f"{stage}BuildImage", type="String",
                                                           description="The codebuild image as specified in https://docs.aws.amazon.com/codebuild/latest/userguide/codebuild-env-ref-available.html. e.g. aws/codebuild/amazonlinux2-x86_64-standard:2.0",
                                                           default="aws/codebuild/standard:4.0")

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
