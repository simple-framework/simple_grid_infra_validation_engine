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
from infra_validation_engine.infra_tests.components.docker import DockerContainerStatusTest


class DeployStageParallelExecutor(ParallelExecutor):
    def __init__(self, cm_rep, lc_rep, container_host_reps, num_threads):
        ParallelExecutor.__init__(self, "Deploy Parallelizer", num_threads)
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.all_hosts = [cm_rep] + lc_rep
        self.host = cm_rep['host']
        self.fqdn = cm_rep['fqdn']
        self.num_threads = num_threads
        self.container_host_reps = container_host_reps
        self.create_pipeline()

    def create_pipeline(self):
        for container_host_rep in self.container_host_reps:
            container_name = container_host_rep['container_name']
            host_rep = container_host_rep['host']
            self.append_to_pipeline(DockerContainerStatusTest(host_rep['host'], host_rep['fqdn'], container_name))


class Deploy(Stage):
    __metaclass__ = StageType

    def __init__(self, cm_rep, lc_rep, augmented_site_level_config_file, num_threads):
        Stage.__init__(self, "Deploy")
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.num_threads = num_threads
        self.augmented_site_level_config_file = augmented_site_level_config_file
        self.augmented_site_level_config = None
        self.container_host_reps = []

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
            DeployStageParallelExecutor(self.cm_rep, self.lc_rep, self.container_host_reps, self.num_threads)
        ])

    def parse_augmented_site_config(self):
        if not 'dns' in self.augmented_site_level_config:
            raise PreConditionNotSatisfiedError("DNS information is missing in {file}".format(
                file=self.augmented_site_level_config_file))
        dns_info = self.augmented_site_level_config['dns']
        for dns in dns_info:
            container_fqdn = dns['container_fqdn']
            host_fqdn = dns['host_fqdn']
            host = self.get_host_rep(host_fqdn)
            self.container_host_reps.append({
                "container_name": container_fqdn,
                "host": host
            })

    def get_host_rep(self, fqdn):
        host_rep = [x for x in self.lc_rep if x['fqdn'] == fqdn]
        return host_rep[0]
