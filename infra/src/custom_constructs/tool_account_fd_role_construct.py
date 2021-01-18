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

from aws_cdk import core
from aws_cdk.aws_iam import PolicyStatement, Role, AccountPrincipal


class ToolAccountFdRoleConstruct(Role):
    """
    This is the tool account role to operate in the target environment
    """

    def __init__(self, scope: core.Construct, id: str, *, tool_account: str, fraud_detector_role_arn: str,
                 role_name=None):
        super().__init__(scope, id, assumed_by=AccountPrincipal(tool_account), role_name=role_name)

        self.add_to_policy(

            PolicyStatement(resources=["*"],
                            actions=["frauddetector:UpdateRuleMetadata",
                                     "frauddetector:CreateVariable",
                                     "frauddetector:BatchCreateVariable",
                                     "frauddetector:PutOutcome",
                                     "frauddetector:UpdateDetectorVersion",
                                     "frauddetector:GetVariables",
                                     "frauddetector:GetDetectors",
                                     "frauddetector:GetRules",
                                     "frauddetector:UpdateDetectorVersionStatus",
                                     "frauddetector:UpdateRuleVersion",
                                     "frauddetector:DescribeModelVersions",
                                     "frauddetector:GetPrediction",
                                     "frauddetector:GetOutcomes",
                                     "frauddetector:GetModels",
                                     "frauddetector:PutModel",
                                     "frauddetector:DeleteEvent",
                                     "frauddetector:BatchGetVariable",
                                     "frauddetector:UpdateModelVersion",
                                     "frauddetector:DescribeDetector",
                                     "frauddetector:PutDetector",
                                     "frauddetector:PutEntityType",
                                     "frauddetector:PutEventType",
                                     "frauddetector:DeleteDetector",
                                     "frauddetector:GetModelVersion",
                                     "frauddetector:CreateModel",
                                     "frauddetector:UpdateModelVersionStatus",
                                     "frauddetector:CreateModelVersion",
                                     "frauddetector:CreateRule",
                                     "frauddetector:GetExternalModels",
                                     "frauddetector:UpdateDetectorVersionMetadata",
                                     "frauddetector:PutExternalModel",
                                     "frauddetector:UpdateVariable",
                                     "frauddetector:GetDetectorVersion",
                                     "frauddetector:DeleteRuleVersion",
                                     "frauddetector:PutLabel",
                                     "frauddetector:CreateDetectorVersion",
                                     "frauddetector:DeleteDetectorVersion"])
        )

        self.add_to_policy(PolicyStatement(resources=[fraud_detector_role_arn], actions=["iam:PassRole"]))
