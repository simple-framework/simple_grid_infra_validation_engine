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

from infra_validation_engine.core import InfraTest
from infra_validation_engine.utils.constants import Constants
from infra_validation_engine.utils.exceptions import ComponentNotInstalledError


class YamlCompilerConstants(Constants):
    YAML_COMPILER_INSTALLATION_DIR = "{SIMPLE_CONFIG_DIR}/yaml_compiler".format(
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
