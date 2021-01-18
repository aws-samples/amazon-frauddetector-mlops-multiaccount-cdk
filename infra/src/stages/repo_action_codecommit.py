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
    aws_codepipeline as codepipeline,
    aws_codecommit,
)
from aws_cdk.aws_codepipeline_actions import CodeCommitSourceAction
from aws_cdk.core import Stack


class RepoActionCodeCommit(CodeCommitSourceAction):

    def __init__(self, scope: core.Construct):
        # Source repo
        stack_scope = Stack.of(scope)
        source_repo_parameter = core.CfnParameter(stack_scope, "CodeCommitRepositoryARN", type="String",
                                                  description="The code codecommit repo arn. e.g. arn:aws:codecommit:us-east-1:111111:test-repo")
        source_repo = source_repo_parameter.value_as_string

        # branch name
        branch_name_parameter = core.CfnParameter(stack_scope, "BranchName", type="String",
                                                  description="The code branch, e.g. master", default="master")
        branch_name = branch_name_parameter.value_as_string

        output_artifact = codepipeline.Artifact("source")
        source_repo = aws_codecommit.Repository.from_repository_arn(stack_scope, id="source",
                                                                    repository_arn=source_repo)
        # source_repo.grant_read(training_pipeline.role)

        super().__init__(output=output_artifact, repository=source_repo, action_name="Source", branch=branch_name)
