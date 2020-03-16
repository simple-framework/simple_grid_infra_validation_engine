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


class Constants:
    def __init__(self):
        pass

    SIMPLE_CONFIG_DIR = "/etc/simple_grid"
    GIT_PKG_NAME = "git"
    SITE_LEVEL_CONFIG_FILE = "/etc/simple_grid/site_config/site_level_config_file.yaml"
    FILESERVER_CONFIG_FILE = "/etc/puppetlabs/puppet/fileserver.conf"
    SIMPLE_SSH_PUB_KEY = "/etc/ssh/simple_host_key.pub"
    SIMPLE_SSH_KEY = "/etc/ssh/simple_host_key"
    SIMPLE_SSH_KEY_FILESERVER = "{SIMPLE_CONFIG_DIR}/simple_host_key.pub".format(SIMPLE_CONFIG_DIR=SIMPLE_CONFIG_DIR)
    SITE_MANIFEST = "/etc/puppetlabs/code/environments/simple/manifests/site.pp"
    PUPPET_AGENT = "/etc/puppetlabs/puppet/puppet.conf"
    STAGE_FILE = "/etc/simple_grid/.stage"
    HOST_CERT_DIR = "{SIMPLE_CONFIG_DIR}/host_certificates".format(SIMPLE_CONFIG_DIR=SIMPLE_CONFIG_DIR)
    NODE_TYPE_FILE = "{SIMPLE_CONFIG_DIR}/.node_type".format(SIMPLE_CONFIG_DIR=SIMPLE_CONFIG_DIR)
    AUGMENTED_SITE_LEVEL_CONFIG_FILE = "{SIMPLE_CONFIG_DIR}/site_config/augmented_site_level_config_file.yaml".format(
        SIMPLE_CONFIG_DIR=SIMPLE_CONFIG_DIR)

class ComponentRepositoryConstants(Constants):
    META_INFO_PREFIX = "meta_info_"
