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
from typing import List, Dict

from aws_cdk import (
    core,
)
from aws_cdk.aws_codepipeline import Pipeline
from deploy_factory_locator import DeployFactoryLocator
from repo_factory_locator import RepoFactoryLocator
from stages.approval_stage import ApprovalStage
from train_factory_locator import TrainFactoryLocator


class MLPipelineConstruct(Pipeline):

    def __init__(self, scope: core.Construct, id: str, repo_type: str, train_stage_type: str,
                 deploy_stage_type: str = None, envs: List[Dict[str, str]] = None):
        super().__init__(scope, id, restart_execution_on_update=True)

        if envs is None or len(envs) == 0:
            envs = [{"EnvName": "Dev", "RequireManualApproval": 0}]

        # Source
        repo_factory_locator = RepoFactoryLocator()
        repo_action = repo_factory_locator.get(repo_type, self)
        self.add_stage(stage_name="Source", actions=[repo_action])

        # # Train
        train_stage = self._get_train_actions_builder(train_stage_type)
        #
        # Deploy
        deploy_stage = self._get_deploy_actions_builder(deploy_stage_type)
        #
        approval_action = ApprovalStage()
        #
        for env in envs:
            env_name = env['EnvName']

            # Manual approval
            require_manual_approval = env['RequireManualApproval']
            self._add_env_stage(env_name, require_manual_approval, repo_action, approval_action, train_stage,
                                deploy_stage)

    def _add_env_stage(self, env_name, require_manual_approval, repo_action, approval_action, train_stage,
                       deploy_stage):
        if require_manual_approval:
            action = approval_action.get_stage(self, env_name, stage="Approval")
            self.add_stage(stage_name=f"PromoteTo{env_name}", actions=[action])
        # Train
        stage_name = "Train"
        train_stage_actions, train_variable_namespace = train_stage.get_stage_actions(self, env_name,
                                                                                      stage_name,
                                                                                      repo_action.action_properties.outputs)
        self.add_stage(stage_name=f"{env_name}{stage_name}", actions=train_stage_actions)
        train_output_variables = train_stage.output_variables
        # Deploy
        if deploy_stage:
            stage_name = "Deploy"
            deploy_stage_actions, deploy_variable_namespace = deploy_stage.get_stage_actions(self,
                                                                                             env_name,
                                                                                             stage_name,
                                                                                             repo_action.action_properties.outputs,
                                                                                             train_output_variables,
                                                                                             train_variable_namespace)
            self.add_stage(stage_name=f"{env_name}{stage_name}", actions=deploy_stage_actions)

    def _get_deploy_actions_builder(self, deploy_stage_type):
        deploy_factory = None
        if deploy_stage_type:
            deploy_factory_locator = DeployFactoryLocator()

            deploy_factory = deploy_factory_locator.get(deploy_stage_type)
        return deploy_factory

    def _get_train_actions_builder(self, train_stage_type):
        train_factory_locator = TrainFactoryLocator()

        train_stage = train_factory_locator.get(train_stage_type)
        return train_stage
