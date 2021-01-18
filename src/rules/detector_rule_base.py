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


class DetectorRuleBase:
    """
    Base class for rule expression
    """

    def validate(self):
        """
        return a list of error messages if not valid. Return None if valid
        :return:
        """
        raise NotImplementedError

    @property
    def rule_id(self):
        raise NotImplementedError

    @property
    def description(self):
        raise NotImplementedError

    @property
    def outcomes(self):
        raise NotImplementedError

    def get_rule_expression(self):
        """
        Returns a rule expression
        :return:
        """
        raise NotImplementedError
