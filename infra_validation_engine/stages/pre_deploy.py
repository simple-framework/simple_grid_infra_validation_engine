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
from infra_validation_engine.infra_tests.components.swarm import SwarmMembershipTest


class SwarmValidator(ParallelExecutor):
    def __init__(self, cm_rep, lc_rep, nodes, num_threads):
        ParallelExecutor.__init__(self, "Docker Swarm Validator", num_threads)
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.all_hosts = [cm_rep] + lc_rep
        self.host = lc_rep[0]['host']
        self.fqdn = lc_rep[0]['fqdn']
        self.nodes = nodes
        self.num_threads = num_threads
        self.create_pipeline()

    def create_pipeline(self):
        self.extend_pipeline([
            SwarmMembershipTest(self.host, self.fqdn, self.nodes)
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

    def pre_condition(self):
        try:
            with open(self.augmented_site_level_config_file, 'r') as augmented_site_level_config_file:
                self.augmented_site_level_config = yaml.safe_load(augmented_site_level_config_file)
        except Exception:
            raise PreConditionNotSatisfiedError("Could not read augmented site level config file from {path}"
                                                .format(path=self.augmented_site_level_config_file))
        self.create_pipeline()

    def create_pipeline(self):
        self.extend_pipeline([
            SwarmValidator(self.cm_rep, self.lc_rep, self.nodes, self.num_threads)
        ])

    def parse_augmented_site_config(self):
        site_infra = self.augmented_site_level_config['site_infrastructure']
        self.nodes = [node['fqdn'] for node in site_infra]