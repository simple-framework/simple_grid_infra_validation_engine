from core import InfraTest
from utils.constants import Constants
from utils.exceptions import DirectoryNotFoundError, PackageNotInstalledError, FileNotCreatedError, FileContentsError

class LightweightComponentPuppetAgentUpdatedTest(InfraTest):
    def __init__(self, host, fqdn, cm_fqdn):
        InfraTest.__init__(self,
        "Lightweight Component - Puppet agent (puppet.conf) is updated Test",
        "Check if {file} is updated on {fqdn}".format(file=Constants.PUPPET_AGENT, fqdn=fqdn),
        host,
        fqdn)

        self.cm_fqdn = cm_fqdn

    def run(self):
        return self.host.file(Constants.PUPPET_AGENT).contains(self.cm_fqdn)

    def fail(self):
        err_msg = "File {file} does not contain CM fqdn.".format(file=Constants.PUPPET_AGENT)

        raise FileContentsError(err_msg)

class LightweightComponentHostkeyTest(InfraTest):
    def __init__(self, host, fqdn, cm_host):
        InfraTest.__init__(self,
        "Lightweight Component - Hostkey is copied Test",
        "Check if {file} is present on {fqdn}".format(file=Constants.PUPPET_AGENT, fqdn=fqdn),
        host,
        fqdn)

        self.cm_host = cm_host

    def run(self):
        if not self.host.file(Constants.SSH_HOST_KEY).exists:
            return False

        return self.cm_host.file(Constants.SSH_HOST_KEY).content_string == self.host.file(Constants.SSH_HOST_KEY).content_string

    def fail(self):
        err_msg = "File {file} does not match CM SSH hostkey or does not exist.".format(file=Constants.PUPPET_AGENT)

        raise FileContentsError(err_msg)