from core import InfraTest
from utils.constants import Constants
from utils.exceptions import DirectoryNotFoundError

class ConfigMasterSimpleGridFolderTest(InfraTest):
  def init(self, host, fqdn):
    InfraTest.init(self,
      "SIMPLE GRID Folder Test",
      "Check if {dir} directory is present on {fqdn}".format(dir=Constants.SIMPLE_CONFIG_DIR, fqdn=fqdn),
      host,
      fqdn)

  def run(self):
    return self.host.file(Constants.SIMPLE_CONFIG_DIR).is_directory

  def fail(self):
    err_msg = "Couldn't find the directory {dir} on {fqdn}".format(dir=Constants.SIMPLE_CONFIG_DIR, fqdn=self.fqdn)

    return DirectoryNotFoundError(err_msg)
