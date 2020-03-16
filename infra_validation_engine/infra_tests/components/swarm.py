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

from infra_validation_engine.core import InfraTestType, InfraTest
from infra_validation_engine.core.standard_tests import FileIsPresentTest
from infra_validation_engine.utils.constants import Constants
import re

class SwarmConstants(Constants):
    SWARM_NETWORK = "simple"
    DNS_FILE = "{simple_config}/.dns.yaml".format(simple_config=Constants.SIMPLE_CONFIG_DIR)
    SWARM_STATUS_FILE = "{simple_config}/.swarm_status".format(simple_config=Constants.SIMPLE_CONFIG_DIR)
    SWARM_INGRESS_NETWORK_NAME = "new-ingress"


class SwarmOverlayNetworkError(Exception):
    """ Raised if swarm overlay network was not found or there was an error with ingress network"""
    pass


class SwarmMissingNodeError(Exception):
    """ Raised if some nodes have not joined the cluster """


class SwarmClusterError(Exception):
    """ Raised if status of cluster cannot be determined"""


class SwarmDNSFileTest(FileIsPresentTest):
    """
    Test if DNS file was generated
    """
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        FileIsPresentTest.__init__(self, "DNS File Presence Test", SwarmConstants.DNS_FILE, host, fqdn)


class SwarmStatusFileTest(FileIsPresentTest):
    """
    Test if SwarmStatus file was generated
    """
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        FileIsPresentTest.__init__(self, "Swarm Status File Presence Test", SwarmConstants.SWARM_STATUS_FILE, host,
                                   fqdn)


class SwarmOverlayNetworkTest(InfraTest):
    """
    Test if swarm overlay network is present on host
    """
    def __init__(self, network, host, fqdn):
        InfraTest.__init__(self, "Swarm Overlay Network Test",
                           "Check of docker network {network} is present on {fqdn}".format(
                               network=network, fqdn=fqdn),
                           host,
                           fqdn)
        self.network = network

    def run(self):
        cmd_str = "docker network ls -q -f 'name={network}' | wc -l".format(network=self.network)
        cmd = self.host.run(cmd_str)
        out = int(cmd.stdout)
        return out == 1

    def fail(self):
        err_msg = "Docker overlay network named {network} was absent on {fqdn}".format(
            network=self.network, fqdn=self.fqdn)
        raise SwarmOverlayNetworkError(err_msg)


class SwarmIngressNetworkTest(SwarmOverlayNetworkTest):
    """
    Test if ingress network is created
    """
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        SwarmOverlayNetworkTest.__init__(self, SwarmConstants.SWARM_INGRESS_NETWORK_NAME, host, fqdn)


class SwarmSimpleOverlayNetworkTest(SwarmOverlayNetworkTest):
    """
    Test is simple overlay network is present
    """
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        SwarmOverlayNetworkTest.__init__(self, SwarmConstants.SWARM_NETWORK, host, fqdn)


class SwarmMembershipTest(InfraTest):
    """
    Test if a node is part of swarm
    """
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn, nodes):
        InfraTest.__init__(self,
                           "Swarm Membership Test",
                           "Test if swarm consists of the following nodes: {nodes}".format(nodes=nodes),
                           host,
                           fqdn)
        self.expected_nodes = set(nodes)

    def run(self):
        cmd_str = "docker node ls"
        cmd = self.host.run(cmd_str)
        self.rc = cmd.rc
        actual_nodes = set()
        if self.rc == 0:
            for node_info in cmd.stdout.split('\n')[1:]:
                node_info = str(node_info).split()
                if not len(node_info) > 0:
                    continue
                if '*' in node_info:
                    actual_nodes.add(node_info[2])
                else:
                    actual_nodes.add(node_info[1])
            missing_nodes = self.expected_nodes - actual_nodes
            self.err = missing_nodes
            return len(missing_nodes) == 0
        return False

    def fail(self):
        if self.rc == 0:
            err_msg = "The following nodes have not joined the Swarm Cluster: {missing}".format(
                missing=', '.join(self.err))
            raise SwarmMissingNodeError(err_msg)
        else:
            err_msg = "Failed to determine status of swarm cluster. 'docker node ls' on {fqdn} exited with {code}".format(
                fqdn=self.fqdn, code=self.rc
            )
            raise SwarmClusterError(err_msg)