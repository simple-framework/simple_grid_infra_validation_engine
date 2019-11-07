from components.yaml_compiler import YamlCompilerInstallationTest
from nodes.config_master import (ConfigMasterSimpleGridFolderTest, ConfigMasterGitInstalledTest, ConfigMasterDockerInstalledTest, ConfigMasterBoltInstalledTest,
                                 ConfigMasterSiteLevelConfigFileTest, ConfigMasterFileServerConfigFileTest)
from core import Stage


class Install(Stage):

    def __init__(self, config_master_host, lightweight_component_hosts):
        Stage.__init__(self, "Install", config_master_host, lightweight_component_hosts)

    def register_tests(self):
        self.infra_tests.extend([
            YamlCompilerInstallationTest(self.config_master_host['host'], self.config_master_host['fqdn']),
            ConfigMasterSimpleGridFolderTest(self.config_master_host['host'], self.config_master_host['fqdn']),
            ConfigMasterGitInstalledTest(self.config_master_host['host'], self.config_master_host['fqdn']),
            ConfigMasterDockerInstalledTest(self.config_master_host['host'], self.config_master_host['fqdn']),
            ConfigMasterBoltInstalledTest(self.config_master_host['host'], self.config_master_host['fqdn']),
            ConfigMasterSiteLevelConfigFileTest(self.config_master_host['host'], self.config_master_host['fqdn']),
            ConfigMasterFileServerConfigFileTest(self.config_master_host['host'], self.config_master_host['fqdn'])
        ])
