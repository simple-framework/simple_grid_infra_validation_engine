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
from infra_validation_engine.core.exceptions import DirectoryNotFoundError, PackageNotFoundError, \
    FileNotFoundError, FileContentsMismatchError


class ConfigMasterSiteLevelConfigFileTest(InfraTest):
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        InfraTest.__init__(self,
                           "Config Master - Site Level Config File Test",
                           "Check if {file} is present on {fqdn}".format(file=Constants.SITE_LEVEL_CONFIG_FILE,
                                                                         fqdn=fqdn),
                           host,
                           fqdn)

    def run(self):
        return self.host.file(Constants.SITE_LEVEL_CONFIG_FILE).is_file

    def fail(self):
        err_msg = "File {file} is not present on {fqdn}".format(file=Constants.SITE_LEVEL_CONFIG_FILE, fqdn=self.fqdn)

        raise FileNotFoundError(err_msg)


class ConfigMasterSSHHostKeyFileTest(InfraTest):
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        InfraTest.__init__(self,
                           "Config Master - FileServer Config File Test",
                           "Check if {file} is present on {fqdn}".format(file=Constants.SIMPLE_SSH_PUB_KEY, fqdn=fqdn),
                           host,
                           fqdn)

    def run(self):
        return self.host.file(Constants.SIMPLE_SSH_PUB_KEY).is_file

    def fail(self):
        err_msg = "File {file} is not present on {fqdn}".format(file=Constants.SIMPLE_SSH_PUB_KEY, fqdn=self.fqdn)

        raise FileNotFoundError(err_msg)


class ConfigMasterConfigStageSetTest(InfraTest):
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        InfraTest.__init__(self,
                           "Config Master - Stage changed to CONFIG Test",
                           "Check if {file} is changed to 'config'".format(file=Constants.STAGE_FILE),
                           host,
                           fqdn)

    def run(self):
        file = self.host.file(Constants.STAGE_FILE)

        if not file.exists:
            return False

        return file.content_string == 'config'

    def fail(self):
        err_msg = "File {file} is not present on {fqdn}".format(file=Constants.STAGE_FILE, fqdn=self.fqdn)

        raise FileContentsMismatchError(err_msg)
