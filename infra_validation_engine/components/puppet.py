import re

from infra_validation_engine.core import InfraTest, InfraTestType
from infra_validation_engine.utils.constants import Constants
from infra_validation_engine.core.standard_tests import (PackageIsInstalledTest, SystemdServiceIsActiveTest,
                                                         DirectoryIsPresentTest, FileIsPresentTest)
from infra_validation_engine.core.exceptions import FileContentsMismatchError


class PuppetConstants(Constants):
    PUPPET_AGENT_PKG_NAME = "puppet-agent"
    PUPPET_AGENT_SVC_NAME = "puppet"
    PUPPET_SERVER_PKG_NAME = "puppetserver"
    PUPPET_SERVER_SVC_NAME = "puppetserver"
    PUPPET_MODULE_NAME = "maany-simple_grid"
    PUPPET_SIMPLE_DIR = "/etc/puppetlabs/code/environments/simple"


class PuppetModuleNotInstalledError(Exception):
    pass


class PuppetAgentInstalledTest(PackageIsInstalledTest):
    """Puppet agent package is installed Test"""
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        PackageIsInstalledTest.__init__(self, "Puppet agent installed Test", PuppetConstants.PUPPET_AGENT_PKG_NAME, host, fqdn)


class PuppetAgentActiveTest(SystemdServiceIsActiveTest):
    """Puppet agent package is active Test"""
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        SystemdServiceIsActiveTest.__init__(self, "Puppet agent running Test", PuppetConstants.PUPPET_AGENT_SVC_NAME, host, fqdn)


class PuppetServerInstalledTest(PackageIsInstalledTest):
    """Puppet server package is installed Test"""
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        PackageIsInstalledTest.__init__(self, "Puppet server installed Test", PuppetConstants.PUPPET_SERVER_PKG_NAME, host, fqdn)


class PuppetServerActiveTest(SystemdServiceIsActiveTest):
    """Puppet server package is active Test"""
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        SystemdServiceIsActiveTest.__init__(self, "Puppet server running Test", PuppetConstants.PUPPET_SERVER_SVC_NAME, host, fqdn)


class PuppetConfTest(InfraTest):
    """Puppet agent (puppet.conf) is updated Test"""
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn, cm_host):
        InfraTest.__init__(self,
                           "Puppet agent configuration Test",
                           "Check if {file} is installed on {fqdn}".format(file=PuppetConstants.PUPPET_AGENT,
                                                                           fqdn=fqdn),
                           host,
                           fqdn)

        self.cm_host = cm_host


    def run(self):
        return self.host.file(PuppetConstants.PUPPET_AGENT).contains(self.cm_host.check_output("hostname"))

    def fail(self):
        err_msg = "File {file} does not contain CM fqdn.".format(file=PuppetConstants.PUPPET_AGENT)

        return FileContentsMismatchError(err_msg)


class PuppetModuleTest(InfraTest):
    """Puppet module is installed Test"""
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        InfraTest.__init__(self,
                           "Puppet module Test",
                           "Check if puppet module is installed on {fqdn}".format(fqdn=fqdn),
                           host, fqdn)

    def run(self):
        cmd = self.host.run("puppet module list | grep {module}".format(module=PuppetConstants.PUPPET_MODULE_NAME))
        module_version = re.search(r'\((.*?)\)', cmd.stdout)
        if module_version:
            self.message = "Puppet module version: {version}".format(version=module_version.group(1))
            return True
        else:
            return False

    def fail(self):
        err_msg = "Puppet module {module} not found on {fqdn}".format(module=PuppetConstants.PUPPET_MODULE_NAME, fqdn=self.fqdn)
        return PuppetModuleNotInstalledError(err_msg)


class PuppetSimpleDirTest(DirectoryIsPresentTest):
    """Puppet SIMPLE dir is present Test"""
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        DirectoryIsPresentTest.__init__(self, "SIMPLE directory Test", PuppetConstants.PUPPET_SIMPLE_DIR, host, fqdn)


class FileServerConfTest(FileIsPresentTest):
    """File Server config file is present Test"""
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        FileIsPresentTest.__init__(self, "File server config file Test", PuppetConstants.FILESERVER_CONFIG_FILE, host, fqdn)