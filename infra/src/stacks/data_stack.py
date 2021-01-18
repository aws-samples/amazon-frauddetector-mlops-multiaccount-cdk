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
from aws_cdk.aws_iam import ArnPrincipal
from aws_cdk.core import CfnParameter

from custom_constructs.data_bucket_construct import DataBucketConstruct


class DataStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket_name_param = CfnParameter(self, f"BucketName", type="String",
                                         description="The name of the bucket to create")
        bucket_name = bucket_name_param.value_as_string

        principal_list_param = CfnParameter(self, f"PrincipalRoleArnCsvList", type="CommaDelimitedList",
                                            description="Comma separated list of principal of arn to have read access to the bucket")
        principal_list = principal_list_param.value_as_list

        self.bucket = DataBucketConstruct(self, id="FraudDetectorDataBucket", bucket_name=bucket_name,
                                          principals=[ArnPrincipal(f) for f in principal_list])
