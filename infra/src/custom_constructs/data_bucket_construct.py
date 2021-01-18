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

from aws_cdk import core
from aws_cdk.aws_iam import PolicyStatement, IPrincipal
from aws_cdk.aws_s3 import Bucket


class DataBucketConstruct(Bucket):

    def __init__(self, scope: core.Construct, id: str, bucket_name, principals: List[IPrincipal]):
        super().__init__(scope, id, bucket_name=bucket_name)

        self.add_to_resource_policy(

            PolicyStatement(resources=[self.bucket_arn], principals=principals,
                            actions=["s3:ListBucket", "s3:GetBucketLocation"])
        )

        self.add_to_resource_policy(

            PolicyStatement(resources=[self.bucket_arn + "/*"], principals=principals,
                            actions=["s3:GetObject"])
        )
