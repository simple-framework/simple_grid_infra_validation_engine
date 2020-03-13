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
from infra_validation_engine.components.bolt import BoltInstallationTest, BoltConfigurationDirectoryTest, \
    BoltConfigurationFileTest, BoltNetworkConfigurationTest
from infra_validation_engine.components.docker import DockerInstallationTest, DockerServiceTest, DockerImageTest, \
    DockerContainerStatusTest
from infra_validation_engine.components.swarm import *

from infra_validation_engine.core import Stage, StageType
from infra_validation_engine.core.executors import ParallelExecutor
from infra_validation_engine.core.standard_tests import PackageIsInstalledTest


class TestExecutor(ParallelExecutor):
    def __init__(self, name, num_threads, cm_host_rep, lc_hosts_rep):
        ParallelExecutor.__init__(self, name, num_threads)
        self.register_infra_test(PackageIsInstalledTest("Git", "git", cm_host_rep['host'], cm_host_rep['fqdn']))
        for lc in lc_hosts_rep:
            self.register_infra_test(PackageIsInstalledTest("Git", "git", lc['host'], lc['fqdn']))


class Test(Stage):
    __metaclass__ = StageType

    def __init__(self, config_master_host, lightweight_component_hosts):
        Stage.__init__(self, "Test", config_master_host, lightweight_component_hosts)

    def pre_condition(self):
        pass

    def create_test_pipeline(self):
        executor = TestExecutor("Test Executor", 4, self.config_master_host, self.lightweight_component_hosts)
        self.executors.append(executor)

    def register_tests(self):
        pass
        # self.infra_tests.extend([
        #     BoltInstallationTest(self.config_master_host['host'], self.config_master_host['fqdn']),
        #     BoltConfigurationDirectoryTest(self.config_master_host['host'], self.config_master_host['fqdn']),
        #     BoltConfigurationFileTest(self.config_master_host['host'], self.config_master_host['fqdn']),
        #     BoltNetworkConfigurationTest(self.config_master_host['host'], self.config_master_host['fqdn'],
        #                                  self.lightweight_component_hosts),
        # ])

        # self.infra_tests.extend([
        #     DockerInstallationTest(self.config_master_host['host'], self.config_master_host['fqdn']),
        #     DockerServiceTest(self.config_master_host['host'], self.config_master_host['fqdn']),
        #     DockerImageTest(self.config_master_host['host'], self.config_master_host['fqdn'], image="maany/*"),
        #     DockerContainerStatusTest(self.config_master_host['host'], self.config_master_host['fqdn'],
        #                               container="condor_cm"),
        # ])

        # self.infra_tests.extend([
        #     SwarmDNSFileTest(self.config_master_host['host'], self.config_master_host['fqdn']),
        #     SwarmOverlayNetworkTest(self.config_master_host['host'], self.config_master_host['fqdn'])
        # ])

    # def execute(self):
    #     executor = TestExecutor("Test Executor",4, self.config_master_host, self.lightweight_component_hosts)
    #     executor.execute()
