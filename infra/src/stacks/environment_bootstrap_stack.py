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
    core
)
from aws_cdk.core import CfnParameter, Aws

from custom_constructs.fraud_detector_service_role_construct import FraudDetectorServiceRoleConstruct
from custom_constructs.tool_account_fd_role_construct import ToolAccountFdRoleConstruct


class EnvironmentBootstrapStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket_path_param = CfnParameter(self, f"BucketPath", type="String",
                                         description="The bucket so fraud detector has read acess. e.g. mybucket/myprefix*. Always specify path, if you need access to all objects specify mybucket/*",
                                         allowed_pattern=".+/.+")
        bucket_path = bucket_path_param.value_as_string

        tool_account_param = CfnParameter(self, f"ToolAccount", type="String",
                                          description="The tool account so it has access to create fraud detector")
        tool_account = tool_account_param.value_as_string

        # 1. Set up FD role in the target environment
        fdrole = FraudDetectorServiceRoleConstruct(self, "FraudDetectorRole", bucket_path=bucket_path,
                                                   role_name=Aws.STACK_NAME + "-" + "FraudDetectorRole")

        # 2. Provide access from the tool account to pass the FD role and create/deploy model & variables
        tool_account = ToolAccountFdRoleConstruct(self, "ToolAccessRole", fraud_detector_role_arn=fdrole.role_arn,
                                                  tool_account=tool_account,
                                                  role_name=Aws.STACK_NAME + "-" + "ToolAccessRole")

        # Output
        core.CfnOutput(self, "FraudDetectorServiceRoleOutput", value=fdrole.role_arn,
                       description="Fraud Detector Service Role")

        core.CfnOutput(self, "ToolsAccountRoleOutput", value=tool_account.role_arn, description="Tool account Role")
