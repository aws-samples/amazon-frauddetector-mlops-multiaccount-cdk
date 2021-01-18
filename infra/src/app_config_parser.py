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

import json
import re


class AppConfigParser:

    def parse_design(self, json_file):
        """
        Constructs the CDK design params from config file
        :param json_file:
        :return:
        """
        with open(json_file, encoding="utf-8") as f:
            json_dict = json.load(f)

        stack_prefix = json_dict["Name"]

        stack_variables = self._get_variables(json_dict)

        stack_design_dict = {}
        for stack_type, stack_params in json_dict["Stacks"].items():
            design_params = stack_params.get("CDKDesign", {})

            formatted_design = {}
            for k, v in design_params.items():
                formatted_key = "_".join([t.lower() for t in re.findall('[A-Z][^A-Z]*', k)])
                formatted_design[formatted_key] = self._variable_substitute(stack_variables, v)

            stack_design_dict[stack_type] = formatted_design

        return stack_prefix, stack_design_dict

    def parse_deploy_params(self, json_file):
        """
        Constructs the CDK parameters which is equal to CFN parameters
        :param json_file:
        :return:
        """
        with open(json_file, encoding="utf-8") as f:
            json_dict = json.load(f)

        stack_prefix = json_dict["Name"]
        stack_variables = self._get_variables(json_dict)

        stack_deploy_dict = {}
        for stack_type, stack_params in json_dict["Stacks"].items():
            deploy_params = stack_params.get("CDKDeploy", {})

            params = []
            for k, v in deploy_params.items():
                if k == "EnvironmentParams":
                    params.extend(self._get_env_parameters(stack_variables, v))
                else:
                    v = self._variable_substitute(stack_variables, v)
                    params.extend(["--parameters", '{}={}'.format(k, v)])

            stack_deploy_dict[stack_type] = params

        return stack_prefix, stack_deploy_dict

    def _get_env_parameters(self, stack_variables, environment_params):
        params = []
        for env_name, env_val in environment_params.items():
            for k, v in env_val.items():
                v = self._variable_substitute(stack_variables, v)
                params.extend(['--parameters', '{}{}={}'.format(env_name, k, v)])

        return params

    def _get_variables(self, json_dict):
        """
        Returns variables
        :param json_dict:
        :return:
        """
        stack_variables = json_dict.get("Variables", {})
        dependent_stack_variables = json_dict.get("DependentVariables", {})
        for k, v in dependent_stack_variables.items():
            stack_variables[k] = self._variable_substitute(stack_variables, v)
        return stack_variables

    def _variable_substitute(self, variables, value):
        # Only substitute if value is string
        if not isinstance(value, str): return value

        for variable, variable_value in variables.items():
            value_to_replace = "${{{}}}".format(variable)

            value = value.replace(value_to_replace, variable_value)

        return value
