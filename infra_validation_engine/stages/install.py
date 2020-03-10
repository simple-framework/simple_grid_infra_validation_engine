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

from infra_validation_engine.components.yaml_compiler import YamlCompilerInstallationTest
from infra_validation_engine.nodes.config_master import (ConfigMasterSimpleGridFolderTest, ConfigMasterGitInstalledTest, ConfigMasterDockerInstalledTest, ConfigMasterBoltInstalledTest,
                                 ConfigMasterSiteLevelConfigFileTest, ConfigMasterFileServerConfigFileTest, ConfigMasterSSHHostKeyFileTest,
                                 ConfigMasterSiteManifestFileTest, ConfigMasterConfigStageSetTest)
from infra_validation_engine.nodes.lightweight_component import LightweightComponentPuppetAgentUpdatedTest, LightweightComponentHostkeyTest
from infra_validatioN_engine.core import Stage, StageType


class Install(Stage):
    __metaclass__ = StageType

    def __init__(self, config_master_host, lightweight_component_hosts):
        Stage.__init__(self, "Install", config_master_host, lightweight_component_hosts)

    def register_tests(self):
        self.infra_tests.extend([
            YamlCompilerInstallationTest(self.config_master_host['host'], self.config_master_host['fqdn']),
            # Config Master Tests
            ConfigMasterSimpleGridFolderTest(self.config_master_host['host'], self.config_master_host['fqdn']),
            ConfigMasterGitInstalledTest(self.config_master_host['host'], self.config_master_host['fqdn']),
            ConfigMasterDockerInstalledTest(self.config_master_host['host'], self.config_master_host['fqdn']),
            ConfigMasterBoltInstalledTest(self.config_master_host['host'], self.config_master_host['fqdn']),
            ConfigMasterSiteLevelConfigFileTest(self.config_master_host['host'], self.config_master_host['fqdn']),
            ConfigMasterFileServerConfigFileTest(self.config_master_host['host'], self.config_master_host['fqdn']),
            ConfigMasterSSHHostKeyFileTest(self.config_master_host['host'], self.config_master_host['fqdn']),
            ConfigMasterSiteManifestFileTest(self.config_master_host['host'], self.config_master_host['fqdn']),
        ])
        # Lightweight Component Tests
        for lc in self.lightweight_component_hosts:
            self.infra_tests.append(LightweightComponentPuppetAgentUpdatedTest(lc['host'], lc['fqdn'], self.config_master_host['host']))
            self.infra_tests.append(LightweightComponentHostkeyTest(lc['host'], lc['fqdn'], self.config_master_host['host']))

        # Check if stage is changed to CONFIG
        self.infra_tests.append(ConfigMasterConfigStageSetTest(self.config_master_host['host'], self.config_master_host['fqdn']))
