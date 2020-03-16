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
from infra_validation_engine.core.exceptions import FileContentsMismatchError


class LightweightComponentHostkeyTest(InfraTest):
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn, cm_host):
        InfraTest.__init__(self,
                           "Lightweight Component - Hostkey is copied Test",
                           "Check if {file} is present on {fqdn}".format(file=Constants.SIMPLE_SSH_PUB_KEY, fqdn=fqdn),
                           host,
                           fqdn)

        self.cm_host = cm_host

    def run(self):
        if not self.host.file(Constants.SIMPLE_SSH_PUB_KEY).exists:
            return False

        return self.cm_host.file(Constants.SIMPLE_SSH_PUB_KEY).content_string == self.host.file(
            Constants.SIMPLE_SSH_PUB_KEY).content_string

    def fail(self):
        err_msg = "File {file} does not match CM SSH hostkey or does not exist.".format(file=Constants.SIMPLE_SSH_PUB_KEY)

        raise FileContentsMismatchError(err_msg)
