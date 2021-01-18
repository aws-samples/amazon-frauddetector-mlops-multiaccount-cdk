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
from aws_cdk import core, aws_sns
from aws_cdk.aws_codepipeline_actions import ManualApprovalAction
from aws_cdk.core import CfnParameter, Stack


class ApprovalStage:

    def __init__(self):
        self._obj = None

    def _set_common_params(self, scope):
        if self._obj is not None: return

        self._obj = object()

        stack_scope = Stack.of(scope)

        self._cfn_approver_email_parameter = CfnParameter(stack_scope, f"EmailApprover", type="String",
                                                          description="The email address of the approver, e.g. myemail@email.com")
        email = self._cfn_approver_email_parameter.value_as_string
        self._topic = aws_sns.Topic(stack_scope, id="approval", display_name=None)
        aws_sns.Subscription(stack_scope, id="notify", topic=self._topic,
                             endpoint=email,
                             protocol=aws_sns.SubscriptionProtocol.EMAIL)

    def get_stage(self, scope: core.Construct, env: str, stage: str):
        self._set_common_params(scope)
        action = ManualApprovalAction(action_name=f"PromoteTo{env}",
                                      notification_topic=self._topic)

        return action
