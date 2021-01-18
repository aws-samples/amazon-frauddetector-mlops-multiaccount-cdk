#!/usr/bin/env python3

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

import argparse
import os
import subprocess

from app import StackType, get_stack_name
from app_config_parser import AppConfigParser


class AppDeployConfig:
    """
    Deploys CDK stack from config file
    """

    def deploy(self, config_file, stack_type, profile, additional_cdk_cmd_args=None):
        app_cmd = '"python {} --configfile {}"'.format(os.path.join(os.path.dirname(__file__), "app.py"), config_file)

        config_parser = AppConfigParser()
        stack_prefix, stack_deploy_dict = config_parser.parse_deploy_params(config_file)

        additional_cdk_cmd_args = additional_cdk_cmd_args or []

        stack = get_stack_name(stack_prefix, stack_type)

        cmd_deploy = ['cdk', '--app',
                      app_cmd,
                      'deploy', stack,
                      "--require-approval", "never",
                      "--profile", '{}'.format(profile)] + additional_cdk_cmd_args + stack_deploy_dict[stack_type]

        self._run_shell(cmd_deploy)

    def _run_shell(self, cmd):
        """
        Runs a shell command
        :param cmd: The cmd to run
        """
        print("Running command\n{}".format(" ".join(cmd)))

        out = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        print(stdout.decode(encoding='utf-8'))
        if stderr:
            error_msg = stderr.decode(encoding='utf-8')
            print(error_msg)
            raise Exception(error_msg)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stacktype", help="The type of stack to deploy", required=True, choices=list(StackType))
    parser.add_argument("--configfile", help="Pass a config File", required=True)
    parser.add_argument("--profile", help="Pass a profile", required=False,
                        default="default")

    args, additional_args = parser.parse_known_args()

    AppDeployConfig().deploy(args.configfile, args.stacktype, args.profile, additional_args)


if __name__ == '__main__':
    main()
