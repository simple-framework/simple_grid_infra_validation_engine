from infra_validation_engine.core import InfraTest, InfraTestType
from infra_validation_engine.core.exceptions import DirectoryNotFoundError, PackageNotFoundError, CommandExecutionError, \
    ServiceNotRunningError, ServiceNotFoundError, FileNotFoundError, PreConditionNotSatisfiedError, NetworkError


class FileIsPresentTest(InfraTest):
    """
    A wrapper test for checking if a file is present on a host
    """

    def __init__(self, name, filepath, host, fqdn):
        InfraTest.__init__(self,
                           name,
                           "Check if {file} is present on {fqdn}".format(file=filepath, fqdn=fqdn),
                           host,
                           fqdn)
        self.filepath = filepath

    def run(self):
        return self.host.file(self.filepath).exists

    def fail(self):
        err_msg = "File {file} was not found on {fqdn}".format(file=self.filepath, fqdn=self.fqdn)
        raise FileNotFoundError(err_msg)


class DirectoryIsPresentTest(InfraTest):
    """
    A wrapper test for checking if a directory is present on a host
    """

    def __init__(self, name, directory, host, fqdn):
        InfraTest.__init__(self,
                           name,
                           "Check if {dir} is present on {fqdn}".format(dir=directory, fqdn=fqdn),
                           host,
                           fqdn)
        self.dir = directory

    def run(self):
        return self.host.file(self.dir).is_directory

    def fail(self):
        err_msg = "Directory {dir} was not found on {fqdn}".format(dir=self.dir, fqdn=self.fqdn)
        raise DirectoryNotFoundError(err_msg)


class PackageIsInstalledTest(InfraTest):
    """
    A wrapper test to check if a package is installed on a host
    """

    def __init__(self, name, package, host, fqdn):
        InfraTest.__init__(self,
                           name,
                           "Check if package {pkg} is installed on {host}".format(pkg=package, host=fqdn),
                           host,
                           fqdn)
        self.pkg = package

    def run(self):
        pkg_found = self.host.package(self.pkg).is_installed
        if not pkg_found:
            return False
        try:
            ver = self.host.package(self.pkg).version
            rel = self.host.package(self.pkg).version
            self.message = "Found {pkg} on {fqdn} with version: {ver} and release: {rel}".format(pkg=self.pkg,
                                                                                                 fqdn=self.fqdn,
                                                                                                 ver=ver,
                                                                                                 rel=rel)
        except Exception as error:
            self.warn = True
            self.message = "Could not find version and release information for {pkg} on {fqdn} due to the following " \
                           "error {error}".format(pkg=self.pkg, fqdn=self.fqdn, error=error.message)
        finally:
            return True

    def fail(self):
        err_msg = "Package {pkg} is not installed on {fqdn}".format(pkg=self.pkg, fqdn=self.fqdn)
        raise PackageNotFoundError(err_msg)


class SystemdServiceIsActiveTest(InfraTest):
    """
    A wrapper test to check if systemctl is-active $service returns active and enabled.
    If service is not active, it is considered a failure
    If service is not enabled, it is raised as a warning
    """

    def __init__(self, name, service, host, fqdn, check_enabled=False):
        if check_enabled:
            description = "Check if systemd unit {svc} is active and enabled on {fqdn}".format(svc=service, fqdn=fqdn)
        else:
            description = "Check if systemd unit {svc} is active on {fqdn}".format(svc=service, fqdn=fqdn)

        InfraTest.__init__(self,
                           name,
                           description,
                           host,
                           fqdn)
        self.check_enabled = check_enabled
        self.svc = service

    def run(self):
        active_cmd_str = "systemctl is-active {svc}".format(svc=self.svc)
        active_cmd = self.host.run(active_cmd_str)
        active_out = active_cmd.stdout.strip()
        is_active = False

        if active_out == "active":
            is_active = True
        elif active_out == "unknown":
            self.rc = 1
            self.err = "Service {svc} was not found on {fqdn}. ".format(svc=self.svc, fqdn=self.fqdn)
            return False
        elif active_out == "inactive":
            self.rc = 2
            self.err = "Service {svc} is not active on {fqdn}. ".format(svc=self.svc, fqdn=self.fqdn)
            return False
        if self.check_enabled:
            enabled_cmd_str = "systemctl is-enabled {svc}".format(svc=self.svc)

            enabled_cmd = self.host.run(enabled_cmd_str)
            if not enabled_cmd.succeeded:
                self.warn = True
                self.message = "Service {svc} is not enabled on {fqdn}. Is it running? {is_active}".format(
                    svc=self.svc,
                    fqdn=self.fqdn,
                    is_active=is_active)
        return True

    def fail(self):
        if self.rc == 1:
            raise ServiceNotFoundError(self.err)
        elif self.rc == 2:
            raise ServiceNotRunningError(self.err)


class CommandExecutionTest(InfraTest):
    """Checks if a command can be successfully executed on a host"""

    def __init__(self, name, command, description, host, fqdn):
        InfraTest.__init__(self,
                           name,
                           description,
                           host,
                           fqdn)

        self.cmd_str = command

    def run(self):
        cmd = self.host.run(self.cmd_str)
        self.out = cmd.stdout
        self.err = cmd.stderr
        self.rc = cmd.rc
        return self.rc == 0

    def fail(self):
        err_msg = "Command {cmd} exited with code {rc} on {fqdn}.\n stderr: {stderr} \nstdout: {stdout}".format(
            cmd=self.cmd_str, fqdn=self.fqdn, rc=self.rc, stdout=self.out, stderr=self.err)
        raise CommandExecutionError(err_msg)


class PingTest(InfraTest):
    """ Checks if a destination host can be pinged from a source host"""
    __metaclass__ = InfraTestType

    def __init__(self, name, destination, description, host, fqdn):
        InfraTest.__init__(self, name, description, host, fqdn)
        self.destination = destination

    def pre_condition(self):
        cmd =self.host.run("ping")
        if cmd.rc == 127:
            raise PreConditionNotSatisfiedError("Command 'ping' was not found on {fqdn}".format(fqdn=self.fqdn))

    def run(self):
        cmd_str = "ping {destination} -c 2".format(destination=self.destination)
        cmd = self.host.run(cmd_str)
        return cmd.rc == 0

    def fail(self):
        err_msg = "Host {dest} cannot be reached from {fqdn}".format(dest=self.destination, fqdn=self.fqdn)
        raise NetworkError(err_msg)


class SSHTest(InfraTest):
    """ Check if a node can be connected via passwordless ssh from the host """
    __metaclass__ = InfraTestType

    def __init__(self, name, destination, description, host, fqdn, key):
        InfraTest.__init__(self, name, description, host, fqdn)
        self.destination = destination
        self.key = key

    def run(self):
        cmd_str = "timeout 1 ssh -i {key} root@{dest}".format(key=self.key, dest=self.destination)
        cmd = self.host.run(cmd_str)
        self.rc = cmd.rc
        self.out = cmd.stdout
        self.err = cmd.stderr
        return self.rc == 0

    def fail(self):
        if self.rc == 124:
            raise NetworkError("Timeout occurred when trying to SSH as root to {dest} from {fqdn}."
                               "Is password required for {key} or {dest} is not part of the known_hosts of {fqdn}"
                               .format(dest=self.destination, fqdn=self.fqdn, key=self.key))
        elif self.rc == 255:
            raise NetworkError("Could not SSH as root to {dest} from {fqdn}. {dest}: Name or Serivce not known"
                               .format(dest=self.destination, fqdn=self.fqdn))
        else:
            raise NetworkError("Could not SSH as root to {dest} from {fqdn}."
                               .format(dest=self.destination, fqdn=self.fqdn))

# class ProcessIsRunningTest()
