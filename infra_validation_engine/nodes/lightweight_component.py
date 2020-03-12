from infra_validation_engine.core import InfraTest, InfraTestType
from infra_validation_engine.utils.constants import Constants
from infra_validation_engine.core.exceptions import FileContentsMismatchError


class LightweightComponentPuppetAgentUpdatedTest(InfraTest):
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn, cm_host):
        InfraTest.__init__(self,
                           "Lightweight Component - Puppet agent (puppet.conf) is updated Test",
                           "Check if {file} is updated on {fqdn}".format(file=Constants.PUPPET_AGENT, fqdn=fqdn),
                           host,
                           fqdn)

        self.cm_host = cm_host

    def run(self):
        return self.host.file(Constants.PUPPET_AGENT).contains(self.cm_host.check_output("hostname"))

    def fail(self):
        err_msg = "File {file} does not contain CM fqdn.".format(file=Constants.PUPPET_AGENT)

        raise FileContentsMismatchError(err_msg)


class LightweightComponentHostkeyTest(InfraTest):
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn, cm_host):
        InfraTest.__init__(self,
                           "Lightweight Component - Hostkey is copied Test",
                           "Check if {file} is present on {fqdn}".format(file=Constants.SSH_HOST_KEY, fqdn=fqdn),
                           host,
                           fqdn)

        self.cm_host = cm_host

    def run(self):
        if not self.host.file(Constants.SSH_HOST_KEY).exists:
            return False

        return self.cm_host.file(Constants.SSH_HOST_KEY).content_string == self.host.file(
            Constants.SSH_HOST_KEY).content_string

    def fail(self):
        err_msg = "File {file} does not match CM SSH hostkey or does not exist.".format(file=Constants.SSH_HOST_KEY)

        raise FileContentsMismatchError(err_msg)
