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
    aws_codestarconnections as codestarconnection,
)
from aws_cdk.aws_codepipeline_actions import BitBucketSourceAction
from aws_cdk.core import Construct, Stack


class RepoActionBitBucket(BitBucketSourceAction):

    def __init__(self, scope: Construct):
        stack_scope = Stack.of(scope)
        # Source connection
        owner_parameter = core.CfnParameter(stack_scope, "Owner", type="String",
                                            description="The owner of the repository, e.g. owner-name")
        owner = owner_parameter.value_as_string

        # branch name
        branch_name_parameter = core.CfnParameter(stack_scope, "BranchName", type="String",
                                                  description="The code branch, e.g. master", default="master")
        branch_name = branch_name_parameter.value_as_string

        # branch name
        repo_parameter = core.CfnParameter(stack_scope, "RepoName", type="String",
                                           description="The repository name in Bit bucket. e.g. ml-training")
        repo = repo_parameter.value_as_string

        # Artifact source
        output_artifact = codepipeline.Artifact("source")

        # Bit bucket connection
        bitbucket_connection = codestarconnection.CfnConnection(scope=scope, id="bitbucket_connection",
                                                                connection_name="bitbucket_connection",
                                                                provider_type="Bitbucket")
        bitbucket_arn = bitbucket_connection.attr_connection_arn

        super().__init__(connection_arn=bitbucket_arn, output=output_artifact, owner=owner,
                         repo=repo, action_name="Source", branch=branch_name)
