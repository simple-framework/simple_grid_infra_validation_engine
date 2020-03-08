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

from infra_validation_engine.core import InfraTest, InfraTestType
from infra_validation_engine.utils.constants import Constants
from infra_validation_engine.utils.exceptions import DirectoryNotFoundError, PackageNotInstalledError


class ConfigMasterSimpleGridFolderTest(InfraTest):
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        InfraTest.__init__(self,
                           "Config Master - SIMPLE GRID Folder Test",
                           "Check if {dir} directory is present on {fqdn}".format(dir=Constants.SIMPLE_CONFIG_DIR, fqdn=fqdn),
                           host,
                           fqdn)

    def run(self):
        return self.host.file(Constants.SIMPLE_CONFIG_DIR).is_directory

    def fail(self):
        err_msg = "Couldn't find the directory {dir} on {fqdn}".format(dir=Constants.SIMPLE_CONFIG_DIR, fqdn=self.fqdn)
        raise DirectoryNotFoundError(err_msg)


class ConfigMasterGitInstalledTest(InfraTest):
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        InfraTest.__init__(self,
                           "Config Master - Git Test",
                           "Check if {pkg} is installed on {fqdn}".format(pkg=Constants.GIT_PKG_NAME, fqdn=fqdn),
                           host,
                           fqdn)

    def run(self):
        return self.host.package(Constants.GIT_PKG_NAME).is_installed

    def fail(self):
        err_msg = "Package {pkg} is not installed on {fqdn}".format(pkg=Constants.GIT_PKG_NAME, fqdn=self.fqdn)

        raise PackageNotInstalledError(err_msg)


class ConfigMasterDockerInstalledTest(InfraTest):
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        InfraTest.__init__(self,
                           "Config Master - Docker Test",
                           "Check if {pkg} is installed on {fqdn}".format(pkg=Constants.DOCKER_PKG_NAME, fqdn=fqdn),
                           host,
                           fqdn)

    def run(self):
        cmd = self.host.run("docker --version")

        return cmd.rc == 0

    def fail(self):
        err_msg = "Package {pkg} is not installed on {fqdn}".format(pkg=Constants.DOCKER_PKG_NAME, fqdn=self.fqdn)

        raise PackageNotInstalledError(err_msg)


class ConfigMasterBoltInstalledTest(InfraTest):
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        InfraTest.__init__(self,
                           "Config Master - Bolt Test",
                           "Check if {pkg} is installed on {fqdn}".format(pkg=Constants.BOLT_PKG_NAME, fqdn=fqdn),
                           host,
                           fqdn)

    def run(self):
        cmd = self.host.run("bolt --version")

        return cmd.rc == 0

    def fail(self):
        err_msg = "Package {pkg} is not installed on {fqdn}".format(pkg=Constants.BOLT_PKG_NAME, fqdn=self.fqdn)

        raise PackageNotInstalledError(err_msg)
