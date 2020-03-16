# coding: utf-8
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import yaml

from infra_validation_engine.core import StageType, Stage, PreConditionNotSatisfiedError
from infra_validation_engine.core.executors import ParallelExecutor
from infra_validation_engine.infra_tests.components.docker import DockerServiceTest
from infra_validation_engine.infra_tests.components.swarm import SwarmMembershipTest
from infra_validation_engine.infra_tests.nodes import AugmentedSiteLevelConfigFileTest


class SwarmValidator(ParallelExecutor):
    def __init__(self, cm_rep, lc_rep, main_lc, nodes, num_threads):
        ParallelExecutor.__init__(self, "Docker Swarm Validator", num_threads)
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.all_hosts = [cm_rep] + lc_rep
        self.host = main_lc['host']
        self.fqdn = main_lc['fqdn']
        self.nodes = nodes
        self.num_threads = num_threads
        self.create_pipeline()

    def create_pipeline(self):
        self.extend_pipeline([
            SwarmMembershipTest(self.host, self.fqdn, self.nodes),

        ])


"""
Docker Daemon Test
Swarm cluster Test
DNS file generation test
swarm status

Augmented Site Level Config for LCs
component repository download
script copy test
host certificate copy test

"""


class PreDeployStageParallelExecutor(ParallelExecutor):
    def __init__(self, cm_rep, lc_rep, num_threads):
        ParallelExecutor.__init__(self, "Install Parallelizer", num_threads)
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.all_hosts = [cm_rep] + lc_rep
        self.host = cm_rep['host']
        self.fqdn = cm_rep['fqdn']
        self.num_threads = num_threads
        self.create_pipeline()

    def create_pipeline(self):
        self.extend_pipeline([

        ])

        for node in self.all_hosts:
            self.extend_pipeline([
                DockerServiceTest(node['host'], node['fqdn']),
                AugmentedSiteLevelConfigFileTest(node['host'], node['fqdn'])
            ])


class Pre_Deploy(Stage):
    __metaclass__ = StageType

    def __init__(self, cm_rep, lc_rep, augmented_site_level_config_file, num_threads):
        Stage.__init__(self, "Pre_Deploy")
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.num_threads = num_threads
        self.augmented_site_level_config_file = augmented_site_level_config_file
        self.augmented_site_level_config = None
        self.nodes = []
        self.main_lc_rep = None

    def pre_condition(self):
        try:
            with open(self.augmented_site_level_config_file, 'r') as augmented_site_level_config_file:
                self.augmented_site_level_config = yaml.safe_load(augmented_site_level_config_file)
        except Exception:
            raise PreConditionNotSatisfiedError("Could not read augmented site level config file from {path}"
                                                .format(path=self.augmented_site_level_config_file))
        self.create_pipeline()

    def create_pipeline(self):
        self.parse_augmented_site_config()
        self.extend_pipeline([
            PreDeployStageParallelExecutor(self.cm_rep, self.lc_rep, self.num_threads),
            SwarmValidator(self.cm_rep, self.lc_rep, self.main_lc_rep, self.nodes, self.num_threads)
        ])

    def parse_augmented_site_config(self):
        site_infra = self.augmented_site_level_config['site_infrastructure']
        self.nodes = [node['fqdn'] for node in site_infra]
        exec_0_lc = [lc for lc in self.augmented_site_level_config['lightweight_components'] if lc['execution_id'] == 0]
        if len(exec_0_lc) >1:
            raise PreConditionNotSatisfiedError("More than 1 lightweight component with execution_id 0 detected in "
                                                "the site level config file: {lc}".format(lc=exec_0_lc))
        else:
            main_lc_fqdn = exec_0_lc[0]['deploy']['node']
            main_lc_rep = [lc for lc in self.lc_rep if lc['fqdn'] == main_lc_fqdn]
            if len(main_lc_rep) == 0:
                raise PreConditionNotSatisfiedError("TestInfra host for {fqdn} was not found".format(
                    fqdn=main_lc_fqdn
                ))
            else:
                self.main_lc_rep = main_lc_rep[0]