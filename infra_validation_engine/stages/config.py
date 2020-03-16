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
from infra_validation_engine.core.standard_tests import FileIsPresentTest
from infra_validation_engine.infra_tests.components.bolt import BoltNetworkConfigurationTest
from infra_validation_engine.infra_tests.components.puppet import PuppetCertTest
from infra_validation_engine.utils.constants import Constants


class SimpleSSHKeyValidator(ParallelExecutor):
    def __init__(self, cm_rep, lc_rep, num_threads):
        ParallelExecutor.__init__(self, "SIMPLE SSH Key Validator", num_threads)
        self.cm_rep = cm_rep
        self.host = cm_rep['host']
        self.fqdn = cm_rep['fqdn']
        self.lc_rep = lc_rep
        self.num_threads = num_threads
        self.create_pipeline()

    def create_pipeline(self):
        self.extend_pipeline([
            FileIsPresentTest("Simple Public SSH Key Test", Constants.SIMPLE_SSH_PUB_KEY, self.host, self.fqdn),
            FileIsPresentTest("Simple Private SSH Key Test", Constants.SIMPLE_SSH_KEY, self.host, self.fqdn),
            FileIsPresentTest("Simple SSH Key Fileserver Test", Constants.SIMPLE_SSH_KEY_FILESERVER, self.host, self.fqdn),
        ])
        for lc in self.lc_rep:
            self.append_to_pipeline(
                FileIsPresentTest("Simple SSH Key Fileserver Test for {node}".format(node=lc['fqdn']),
                                  Constants.SIMPLE_SSH_KEY_FILESERVER, lc['host'], lc['fqdn']),
            )


class PuppetValidator(ParallelExecutor):
    def __init__(self, cm_rep, lc_rep, num_threads):
        ParallelExecutor.__init__(self, "Puppet Cert Validator", num_threads)
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.all_hosts = [cm_rep] + lc_rep
        self.host = cm_rep['host']
        self.fqdn = cm_rep['fqdn']
        self.num_threads = num_threads
        self.create_pipeline()

    def create_pipeline(self):
        for lc in self.lc_rep:
            self.append_to_pipeline(PuppetCertTest(lc['fqdn'], self.host, self.fqdn))


class Config(Stage):
    """ Validate config right after signing of certificates """
    __metaclass__ = StageType

    def __init__(self, cm_rep, lc_rep, num_threads):
        Stage.__init__(self, "Config")
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.num_threads = num_threads
        self.create_pipeline()

    def create_pipeline(self):
        self.extend_pipeline([
            PuppetValidator(self.cm_rep, self.lc_rep, self.num_threads),
            SimpleSSHKeyValidator(self.cm_rep, self.lc_rep, self.num_threads),
            BoltNetworkConfigurationTest(self.cm_rep['host'], self.cm_rep['fqdn'], self.lc_rep)
        ])