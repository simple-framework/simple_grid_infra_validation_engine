from core import InfraTest
from utils.constants import Constants
from utils.exceptions import DirectoryNotFoundError, PackageNotInstalledError, FileNotCreatedError, FileContentsError

class LightweightComponentPuppetAgentUpdatedTest(InfraTest):
    def __init__(self, host, fqdn, cm_fqdn):
        InfraTest.__init__(self,
        "Lightweight Component - Puppet agent (puppet.conf) is updated Test",
        "Check if {file} is present on {fqdn}".format(file=Constants.PUPPET_AGENT, fqdn=fqdn),
        host,
        fqdn)

        self.cm_fqdn = cm_fqdn

    def run(self):
        print("FQDNNNNNNNNNNNNNNNNNN {cm}".format(cm=self.cm_fqdn))
        print(self.host.file(Constants.PUPPET_AGENT).contains(self.cm_fqdn))
        return self.host.file(Constants.PUPPET_AGENT).contains(self.cm_fqdn)

    def fail(self):
        err_msg = "File {file} does not contain CM fqdn.".format(file=Constants.PUPPET_AGENT)

        raise FileContentsError(err_msg)