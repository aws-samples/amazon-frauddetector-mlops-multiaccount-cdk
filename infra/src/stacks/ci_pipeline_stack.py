# *****************************************************************************
# * Copyright 2019 Amazon.com, Inc. and its affiliates. All Rights Reserved.  *
#                                                                             *
# Licensed under the Amazon Software License (the "License").                 *
#  You may not use this file except in compliance with the License.           *
# A copy of the License is located at                                         *
#                                                                             *
#  http://aws.amazon.com/asl/                                                 *
#                                                                             *
#  or in the "license" file accompanying this file. This file is distributed  *
#  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either  *
#  express or implied. See the License for the specific language governing    *
#  permissions and limitations under the License.                             *
# *****************************************************************************

from aws_cdk import (
    core
)
from aws_cdk.core import CfnParameter

from custom_constructs.ci_pipeline_construct import CIPipelineConstruct


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

class CIPipelineStack(core.Stack):
    """
    This sets up the CI pipeline that builds and tests python and cdk.
    """

    def __init__(self, scope: core.Construct, id: str, *, repo_type: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        cfn_buildspec_parameter = CfnParameter(self, "BuildSpec", default="build/buildspec.build.yml",
                                               type="String",
                                               description="The name of the codebuild spec file. e.g. codebuild/buildspec.yml")

        buildspec = cfn_buildspec_parameter.value_as_string

        cfn_build_image_parameter = CfnParameter(self, "BuildImage", type="String",
                                                 description="The codebuild image as specified in https://docs.aws.amazon.com/codebuild/latest/userguide/codebuild-env-ref-available.html. e.g. aws/codebuild/amazonlinux2-x86_64-standard:2.0",
                                                 default="aws/codebuild/standard:4.0")
        build_image = cfn_build_image_parameter.value_as_string

        CIPipelineConstruct(self, id="FDCIPipeline", repo_type=repo_type, build_image=build_image, buildspec=buildspec)
