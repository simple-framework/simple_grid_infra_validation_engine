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
from infra_validation_engine.core.standard_tests import FileIsPresentTest
from infra_validation_engine.utils.constants import Constants


class AugmentedSiteLevelConfigFileTest(FileIsPresentTest):
    def __init__(self, host, fqdn):
        FileIsPresentTest.__init__(self,
                                   "Augmented Site Level Config File Test on {fqdn}".format(fqdn=fqdn),
                                   Constants.AUGMENTED_SITE_LEVEL_CONFIG_FILE,
                                   host,
                                   fqdn)
