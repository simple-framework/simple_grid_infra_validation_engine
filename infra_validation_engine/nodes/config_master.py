from core import InfraTest
from utils.constants import Constants
from utils.exceptions import DirectoryNotFoundError, PackageNotInstalledError, FileNotCreatedError

class ConfigMasterSimpleGridFolderTest(InfraTest):
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

class ConfigMasterSiteLevelConfigFileTest(InfraTest):
    def __init__(self, host, fqdn):
        InfraTest.__init__(self,
        "Config Master - Site Level Config File Test",
        "Check if {file} is present on {fqdn}".format(file=Constants.SITE_LEVEL_CONFIG_FILE, fqdn=fqdn),
        host,
        fqdn)

    def run(self):
        cmd = self.host.run("test -f {file}".format(file=Constants.SITE_LEVEL_CONFIG_FILE))

        return cmd.rc == 0

    def fail(self):
        err_msg = "File {file} is not present on {fqdn}".format(file=Constants.SITE_LEVEL_CONFIG_FILE, fqdn=self.fqdn)

        raise FileNotCreatedError(err_msg)

class ConfigMasterFileServerConfigFileTest(InfraTest):
    def __init__(self, host, fqdn):
        InfraTest.__init__(self,
        "Config Master - FileServer Config File Test",
        "Check if {file} is present on {fqdn}".format(file=Constants.FILESERVER_CONFIG_FILE, fqdn=fqdn),
        host,
        fqdn)

    def run(self):
        cmd = self.host.run("test -f {file}".format(file=Constants.FILESERVER_CONFIG_FILE))

        return cmd.rc == 0

    def fail(self):
        err_msg = "File {file} is not present on {fqdn}".format(file=Constants.FILESERVER_CONFIG_FILE, fqdn=self.fqdn)

        raise FileNotCreatedError(err_msg)

class ConfigMasterSSHHostKeyFileTest(InfraTest):
    def __init__(self, host, fqdn):
        InfraTest.__init__(self,
        "Config Master - FileServer Config File Test",
        "Check if {file} is present on {fqdn}".format(file=Constants.SSH_HOST_KEY, fqdn=fqdn),
        host,
        fqdn)

    def run(self):
        cmd = self.host.run("test -f {file}".format(file=Constants.SSH_HOST_KEY))

        return cmd.rc == 0

    def fail(self):
        err_msg = "File {file} is not present on {fqdn}".format(file=Constants.SSH_HOST_KEY, fqdn=self.fqdn)

        raise FileNotCreatedError(err_msg)