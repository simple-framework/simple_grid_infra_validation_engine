from components.yaml_compiler import YamlCompilerInstallationTest
from core import Stage


class Install(Stage):

    def __init__(self, config_master_host, lightweight_component_hosts):
        Stage.__init__(self, "Install", config_master_host, lightweight_component_hosts)

    def register_tests(self):
        self.infra_tests.append(YamlCompilerInstallationTest(self.config_master_host['host'], self.config_master_host['fqdn']))



