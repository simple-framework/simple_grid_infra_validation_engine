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
from infra_validation_engine.core.executors import ParallelExecutor, SerialExecutor
from infra_validation_engine.infra_tests.components.puppet import PuppetAgentInstalledTest, PuppetAgentActiveTest, \
    PuppetServerInstalledTest, PuppetServerActiveTest, PuppetConfTest, PuppetModuleTest


class NetworkAndPuppet(ParallelExecutor):

    def __init__(self, cm_rep, lc_rep, num_threads):
        ParallelExecutor.__init__(self, "Network and Puppet Status Checker", num_threads)
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.create_pipeline()

    def create_pipeline(self):
        for lc in self.lc_rep:
            self.append_to_pipeline(PuppetAgentInstalledTest(lc['host'], lc['fqdn']))

# class PuppetOnCM(SerialExecutor):
#
#     def __init__(self, cm_rep):
#         SerialExecutor.__init__(self, "Puppet Status Checker for Config Master")
#         self.host = cm_rep['host']
#         self.fqdn = cm_rep['fqdn']
#
#     def create_pipeline(self):
#         self.extend_pipeline([
#
#         ])


class PreInstallParallelExecutor(ParallelExecutor):
    """
    Stage is serial executor by default, we need to insert a parallel
    executor for pre_install given the nature of tests
    """
    def __init__(self, cm_rep, lc_rep, num_threads):
        ParallelExecutor.__init__(self, " Pre Install Parallelizer", num_threads)
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.host = cm_rep['host']
        self.fqdn = cm_rep['fqdn']
        self.create_pipeline()

    def create_pipeline(self):
        self.extend_pipeline([
            PuppetAgentInstalledTest(self.host, self.fqdn),
            PuppetAgentActiveTest(self.host, self.fqdn),
            PuppetServerInstalledTest(self.host, self.fqdn),
            PuppetServerActiveTest(self.host, self.fqdn),
            PuppetModuleTest(self.host, self.fqdn),
            NetworkAndPuppet(self.cm_rep, self.lc_rep, self.num_threads)
        ])


class Pre_Install(Stage):
    __metaclass__ = StageType

    def __init__(self, cm_rep, lc_rep, num_threads):
        Stage.__init__(self, "Pre_Install")
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.num_threads = num_threads
        self.create_pipeline()

    def create_pipeline(self):
        self.append_to_pipeline(PreInstallParallelExecutor(self.cm_rep, self.lc_rep, self.num_threads))
