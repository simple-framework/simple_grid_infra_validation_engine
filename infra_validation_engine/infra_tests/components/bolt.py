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
import re
from infra_validation_engine.core import InfraTestType, InfraTest
from infra_validation_engine.core.standard_tests import PackageIsInstalledTest, DirectoryIsPresentTest, \
    FileIsPresentTest
from infra_validation_engine.utils.constants import Constants
from infra_validation_engine.core.exceptions import PackageNotFoundError, DirectoryNotFoundError, FileNotFoundError, \
    NetworkError


class BoltConstants(Constants):
    BOLT_PKG_NAME = "bolt"
    BOLT_CONFIG_DIRECTORY = "/root/.puppetlabs/bolt"
    BOLT_CONFIG_FILE = "{BOLT_CONFIG_DIRECTORY}/bolt.yaml".format(BOLT_CONFIG_DIRECTORY=BOLT_CONFIG_DIRECTORY)


class BoltInstallationTest(PackageIsInstalledTest):
    """
    Check if Bolt is installed
    """
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        PackageIsInstalledTest.__init__(self,
                                        "Bolt Installation Test",
                                        "puppet-bolt",
                                        host,
                                        fqdn)


class BoltConfigurationDirectoryTest(DirectoryIsPresentTest):
    """
    Checks if Bolt config dir is present
    """
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        DirectoryIsPresentTest.__init__(self,
                                        "Bolt Configuration Directory Test",
                                        BoltConstants.BOLT_CONFIG_DIRECTORY,
                                        host,
                                        fqdn)


class BoltConfigurationFileTest(FileIsPresentTest):
    """
    Check if Bolt Config File is present
    """
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        FileIsPresentTest.__init__(self,
                                   "Bolt Configuration File Test",
                                   BoltConstants.BOLT_CONFIG_FILE,
                                   host,
                                   fqdn)


class BoltNetworkConfigurationTest(InfraTest):
    """
    Check if Bolt can connect to all LCs. Bolt is parallel by design, so leverage that
    """
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn, lc_hosts_rep):
        self.lc_hosts_rep = lc_hosts_rep
        self.targets = [x['fqdn'] for x in self.lc_hosts_rep]
        self.targets_str = ','.join(self.targets)
        InfraTest.__init__(self,
                           "Bolt Network Configuration Test",
                           "Check if Bolt can connect from {fqdn} to {targets_str}".format(
                               targets_str=self.targets_str,
                               fqdn=fqdn
                           ),
                           host,
                           fqdn)

    def run(self):
        bolt_cmd = "bolt command run 'pwd' --targets {targets}".format(targets=self.targets_str)
        cmd = self.host.run(bolt_cmd)
        self.err = cmd.stderr
        return cmd.succeeded

    def fail(self):
        failed_targets = self.parse_bolt_stderr()
        err_msg = "Bolt cannot connect from {fqdn} to following hosts: {failed_targets}".format(
            bolt_config=BoltConstants.BOLT_CONFIG_FILE, fqdn=self.fqdn, failed_targets=', '.join(failed_targets))
        raise NetworkError(err_msg)

    def parse_bolt_stderr(self):
        err = self.err
        failed_targets = []
        pattern = '"target":"(\w*)"'
        for line in err.split("\n"):
            if line.strip().startswith('{') and "CONNECT_ERROR" in line:
                search = re.search(pattern, line)
                target = search.group(1)
                failed_targets.append(target)
        return failed_targets
