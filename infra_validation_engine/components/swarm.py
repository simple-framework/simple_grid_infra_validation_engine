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
from infra_validation_engine.core import InfraTestType
from infra_validation_engine.core.standard_tests import FileIsPresentTest
from infra_validation_engine.utils.constants import Constants


class SwarmConstants(Constants):
    SWARM_NETWORK = "simple"
    DNS_FILE = "{simple_config}/dns.yaml".format(simple_config=Constants.SIMPLE_CONFIG_DIR)
    SWARM_STATUS_FILE = "{simple_config}/.swarm_status".format(simple_config=Constants.SIMPLE_CONFIG_DIR)
    SWARM_INGRESS_NETWORK_NAME = "new-ingress"


class SwarmDNSFileTest(FileIsPresentTest):
    """
    Test if DNS file was generated
    """
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        FileIsPresentTest.__init__(self, "DNS File Presence Test", SwarmConstants.DNS_FILE, host, fqdn)

