from infra_validation_engine.core import InfraTest
from infra_validation_engine.utils.constants import Constants
from infra_validation_engine.utils.exceptions import ComponentNotInstalledError


class YamlCompilerConstants(Constants):
    YAML_COMPILER_INSTALLATION_DIR = "{SIMPLE_CONFIG_DIR}/simple_grid_yaml_compiler".format(
        SIMPLE_CONFIG_DIR=Constants.SIMPLE_CONFIG_DIR
    )


class YamlCompilerInstallationTest(InfraTest):

    def __init__(self, host, stage):
        InfraTest.__init__(self, host)
        self.stage = stage

    def run(self):
        self.host.directory(YamlCompilerConstants.YAML_COMPILER_INSTALLATION_DIR)

    def fail(self):
        raise ComponentNotInstalledError("Could not find the simple_grid_yaml_compiler directory at {path}".format(
            path=YamlCompilerConstants.YAML_COMPILER_INSTALLATION_DIR
        ))
