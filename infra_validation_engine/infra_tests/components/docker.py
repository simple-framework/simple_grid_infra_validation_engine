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
from infra_validation_engine.core.exceptions import PackageNotFoundError, ServiceNotRunningError, \
    CommandExecutionError


class DockerConstants(Constants):
    DOCKER_PKG_NAME = "docker-ce"


class DockerImageNotFoundError(Exception):
    """ Raised if Docker Image is not found"""
    pass


class DockerContainerNotFoundError(Exception):
    """ Raised if container is not present on a node """
    pass


class DockerContainerNotRunningError(Exception):
    """ Raised if container is present but is not running """
    pass


class DockerInstallationTest(InfraTest):
    """Test if Docker is installed on the nodes"""
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        InfraTest.__init__(self,
                           "Docker Installation Test",
                           "Check if {pkg} is installed on {fqdn}".format(pkg=DockerConstants.DOCKER_PKG_NAME,
                                                                          fqdn=fqdn),
                           host,
                           fqdn)

    def run(self):
        cmd = self.host.run("docker --version")

        return cmd.rc == 0

    def fail(self):
        err_msg = "Package {pkg} is not installed on {fqdn}".format(pkg=DockerConstants.DOCKER_PKG_NAME, fqdn=self.fqdn)

        raise PackageNotFoundError(err_msg)


class DockerServiceTest(InfraTest):
    """
    Test if docker is running on a node
    """
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        InfraTest.__init__(self,
                           "Docker Service Test",
                           "Check if docker is running on {fqdn}".format(fqdn=fqdn),
                           host,
                           fqdn)

    def run(self):
        cmd = self.host.run("docker ps -a")
        return cmd.rc == 0

    def fail(self):
        err_msg = "Docker is not running on {fqdn}".format(fqdn=self.fqdn)

        raise ServiceNotRunningError(err_msg)


class DockerImageTest(InfraTest):
    """
    Check if a given image is present on the host
    """

    def __init__(self, host, fqdn, image):
        InfraTest.__init__(self,
                           "Docker Image Test",
                           "Check if {image} is present on {fqdn}".format(image=image, fqdn=fqdn),
                           host,
                           fqdn)
        self.image = image

    def run(self):
        cmd_str = 'docker image ls -q -f "reference={image}"'.format(image=self.image)
        cmd = self.host.run(cmd_str)
        print cmd.rc, cmd.stdout == ""
        if cmd.stdout == "":
            return False

        self.out = cmd.stdout.split("\n")
        print self.out

        # stdout containers one extra line
        is_single_image = len(self.out) == 2

        if is_single_image:
            self.out = self.out
            self.message = "The Image ID for {image} on {fqdn} is {id}".format(image=self.image, fqdn=self.fqdn,
                                                                               id=self.out)
        else:
            self.message = "Multiple docker images found for {image}".format(image=self.image)
            self.warn = True

        return True

    def fail(self):
        err_msg = "Docker Image {image} was not found on {fqdn}".format(image=self.image, fqdn=self.fqdn)
        raise DockerImageNotFoundError(err_msg)


class DockerContainerStatusTest(InfraTest):
    """ Tests if container is running """

    def __init__(self, host, fqdn, container):
        InfraTest.__init__(self,
                           "Docker Container Status Test",
                           "Check if {container} is running on {fqdn}".format(container=container, fqdn=fqdn),
                           host,
                           fqdn)
        self.container = container
        self.cmd_str = ""

    def run(self):
        cmd_str = "docker inspect -f '{{.State.Running}}' " + "{container}".format(container=self.container)
        cmd = self.host.run(cmd_str)
        self.rc = cmd.rc
        self.err = cmd.stderr
        self.out = cmd.stdout
        test_status = False
        if self.out.strip() == "true":
            test_status = True
        return test_status

    def fail(self):
        if self.rc == 1:
            err_msg = "Container {container} could not be found on {fqdn}".format(container=self.container,
                                                                                  fqdn=self.fqdn)
            raise DockerContainerNotFoundError(err_msg)
        elif self.rc == 127:
            err_msg = "Command {cmd_str} could not be executed on {fqdn}".format(cmd_str=self.cmd_str, fqdn=self.fqdn)
            raise CommandExecutionError(err_msg)
        elif self.rc == 0:
            err_msg = "Docker container {container} is present but is not running on {fqdn}".format(
                container=self.container,
                fqdn=self.fqdn)
            raise DockerContainerNotRunningError(err_msg)

# class DockerContainerSanityTest(InfraTest):
#     """
#     Executes sanity check script for a container
#     """
#     pass
