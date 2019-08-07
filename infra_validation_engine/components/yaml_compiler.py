from core import InfraTest
from utils.constants import Constants
from utils.exceptions import ComponentNotInstalledError


class YamlCompilerConstants(Constants):
    YAML_COMPILER_INSTALLATION_DIR = "{SIMPLE_CONFIG_DIR}/simple_grid_yaml_compiler".format(
        SIMPLE_CONFIG_DIR=Constants.SIMPLE_CONFIG_DIR
    )


class YamlCompilerInstallationTest(InfraTest):

    def __init__(self, host, fqdn):
        InfraTest.__init__(self, "Yaml Compiler Installation Test",
                           "Check if YAML compiler was installed on {fqdn}".format(fqdn=fqdn),
                           host, fqdn)

    def run(self):
        return self.host.file(YamlCompilerConstants.YAML_COMPILER_INSTALLATION_DIR).is_directory

    def fail(self):
        raise ComponentNotInstalledError("Could not find the simple_grid_yaml_compiler directory at {path}".format(
            path=YamlCompilerConstants.YAML_COMPILER_INSTALLATION_DIR
        ))
