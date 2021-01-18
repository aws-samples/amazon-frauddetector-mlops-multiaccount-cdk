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

from aws_cdk import (
    core,
    aws_codepipeline_actions)
from aws_cdk.aws_codepipeline import Pipeline
from aws_cdk.aws_iam import PolicyStatement, AccountPrincipal
from aws_cdk.core import Stack

from repo_factory_locator import RepoFactoryLocator
from stages.generic_stage_codebuild import GenericStageCodeBuild


class CIPipelineConstruct(Pipeline):

    def __init__(self, scope: core.Construct, id: str, repo_type: str, buildspec: str, build_image: str) -> None:
        super().__init__(scope, id,
                         restart_execution_on_update=True)

        # Source
        repo_factory_locator = RepoFactoryLocator()
        repo_action = repo_factory_locator.get(repo_type, self)
        self.add_stage(stage_name="Source", actions=[repo_action])

        # Build Test
        build_test_actions, _ = GenericStageCodeBuild().get_stage_actions(scope, "BuildTest",
                                                                          repo_action.action_properties.outputs,
                                                                          buildspec_file=buildspec,
                                                                          build_image=build_image)
        self.add_stage(stage_name="BuildTest", actions=build_test_actions)

        # Publish artifacts
        outputs = []
        for build_action in build_test_actions:
            outputs.extend(build_action.action_properties.outputs)
        publish_action = aws_codepipeline_actions.S3DeployAction(bucket=self.artifact_bucket,
                                                                 object_key="BuildArtifacts",
                                                                 action_name="PublishArtifacts", input=outputs[0],
                                                                 extract=True

                                                                 )

        self.add_stage(stage_name="PublishArtifacts", actions=[publish_action])

        # Add decrypt permissions
        self.artifact_bucket.encryption_key.add_to_resource_policy(
            PolicyStatement(principals=[AccountPrincipal(Stack.of(self).account)],
                            actions=["kms:Decrypt"]
                            , resources=["*"]
                            )
        )
