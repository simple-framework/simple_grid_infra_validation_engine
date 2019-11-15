from components.yaml_compiler import YamlCompilerInstallationTest
from nodes.config_master import (ConfigMasterSimpleGridFolderTest, ConfigMasterGitInstalledTest, ConfigMasterDockerInstalledTest, ConfigMasterBoltInstalledTest,
                                 ConfigMasterSiteLevelConfigFileTest, ConfigMasterFileServerConfigFileTest, ConfigMasterSSHHostKeyFileTest,
                                 ConfigMasterSiteManifestFileTest, ConfigMasterConfigStageSetTest)
from nodes.lightweight_component import LightweightComponentPuppetAgentUpdatedTest, LightweightComponentHostkeyTest
from core import Stage


class Install(Stage):

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
