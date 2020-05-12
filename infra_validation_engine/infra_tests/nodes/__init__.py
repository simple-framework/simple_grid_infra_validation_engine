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
from infra_validation_engine.core.exceptions import CommandExecutionError
from infra_validation_engine.core.standard_tests import FileIsPresentTest
from infra_validation_engine.utils.constants import Constants


class InvalidSELinuxConfiguration(Exception):
    """
    Raised if sestatus output is not the expected output i.e
    SELinux was enabled while we checked for it to be disabled and vice versa
    """
    pass


class AugmentedSiteLevelConfigFileTest(FileIsPresentTest):
    def __init__(self, host, fqdn):
        FileIsPresentTest.__init__(self,
                                   "Augmented Site Level Config File Test on {fqdn}".format(fqdn=fqdn),
                                   Constants.AUGMENTED_SITE_LEVEL_CONFIG_FILE,
                                   host,
                                   fqdn)


class SELinuxTest(InfraTest):
    def __init__(self, name, se_status, description, host, fqdn):
        InfraTest.__init__(self, name, description, host, fqdn)
        self.se_status = se_status
        self.cmd_str = "sestatus"
        self.host_se_status = "undetermined"

    def run(self):
        cmd = self.host.run(self.cmd_str)
        self.out = cmd.stdout
        self.err = cmd.stderr
        self.rc = cmd.rc
        self.host_se_status = self.out.split(':')[1].strip()
        return self.host_se_status == self.se_status

    def fail(self):
        if self.rc != 0:
            err_msg = "Could not execute {command} on {host}".format(
                command=self.cmd_str, host=self.fqdn
            )
            raise CommandExecutionError(err_msg)
        else:
            err_msg = "SELinux was {host_se_status} on {host}. The expected SELinux status is {se_status}".format(
                se_status=self.se_status,
                host_se_status=self.host_se_status,
                host=self.fqdn
            )
            raise InvalidSELinuxConfiguration(err_msg)
