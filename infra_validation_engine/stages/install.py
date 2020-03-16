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

from infra_validation_engine.core import Stage, StageType
from infra_validation_engine.core.executors import ParallelExecutor
from infra_validation_engine.core.standard_tests import PackageIsInstalledTest, FileIsPresentTest
from infra_validation_engine.infra_tests.components.bolt import BoltInstallationTest, BoltConfigurationDirectoryTest, \
    BoltConfigurationFileTest
from infra_validation_engine.infra_tests.components.docker import DockerInstallationTest
from infra_validation_engine.infra_tests.components.puppet import PuppetServerInstallationTest, PuppetFirewallPortTest, \
    SimplePuppetEnvTest, PuppetConfTest, PuppetServerServiceTest, PuppetFileServerConfTest, PuppetCertTest
from infra_validation_engine.utils.constants import Constants


class BoltValidator(ParallelExecutor):
    def __init__(self, cm_rep, num_threads):
        ParallelExecutor.__init__(self, "Bolt Validator", num_threads)
        self.host = cm_rep['host']
        self.fqdn = cm_rep['fqdn']
        self.create_pipeline()

    def create_pipeline(self):
        self.extend_pipeline([
            BoltInstallationTest(self.host, self.fqdn),
            BoltConfigurationDirectoryTest(self.host, self.fqdn),
            BoltConfigurationFileTest(self.host, self.fqdn),
        ])


class GitAndDockerInstallationValidator(ParallelExecutor):
    def __init__(self, all_hosts, num_threads):
        ParallelExecutor.__init__(self, "Git and Docker Installation Validator", num_threads)
        self.nodes = all_hosts
        self.create_pipeline()

    def create_pipeline(self):
        for node in self.nodes:
            self.extend_pipeline([
                DockerInstallationTest(node['host'], node['fqdn']),
                PackageIsInstalledTest("Git Installation Test for {fqdn}".format(fqdn=node['fqdn']),
                                       "git", node['host'], node['fqdn'])
            ])


class InstallStageParallelExecutor(ParallelExecutor):
    """
    Stage is serial executor by default, we need to insert a parallel
    executor for pre_install given the nature of tests
    """

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
            PuppetServerInstallationTest(self.host, self.fqdn),
            PuppetServerServiceTest(self.host, self.fqdn),
            PuppetFileServerConfTest(self.host, self.fqdn),
            GitAndDockerInstallationValidator(self.all_hosts, self.num_threads),
            SimplePuppetEnvTest(self.host, self.fqdn),
            PuppetFirewallPortTest(self.host, self.fqdn),
            BoltValidator(self.cm_rep, self.num_threads)
        ])
        for node in self.all_hosts:
            self.extend_pipeline([
                FileIsPresentTest("SIMPLE node_type file test for {fqdn}".format(fqdn=node['fqdn']),
                                  Constants.NODE_TYPE_FILE,
                                  node['host'],
                                  node['fqdn']
                                  ),
                PuppetConfTest(self.host, node['host'], node['fqdn'])
            ])

        for lc in self.lc_rep:
            self.append_to_pipeline(PuppetCertTest(lc['fqdn'], self.host, self.fqdn))


class Install(Stage):
    """ Everything until signing of certificates """
    __metaclass__ = StageType

    def __init__(self, cm_rep, lc_rep, num_threads):
        Stage.__init__(self, "Install")
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.num_threads = num_threads
        self.create_pipeline()

    def create_pipeline(self):
        self.extend_pipeline([
            InstallStageParallelExecutor(self.cm_rep, self.lc_rep, self.num_threads)
        ])
