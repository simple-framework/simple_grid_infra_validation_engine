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
    DOCKER_PKG_NAME = "docker"
    BOLT_PKG_NAME = "bolt"
    SITE_LEVEL_CONFIG_FILE = "/etc/simple_grid/site_config/site_level_config_file.yaml"
    FILESERVER_CONFIG_FILE = "/etc/puppetlabs/puppet/fileserver.conf"
    SSH_HOST_KEY = "/etc/ssh/simple_host_key.pub"
    SITE_MANIFEST = "/etc/puppetlabs/code/environments/simple/manifests/site.pp"
    PUPPET_AGENT = "/etc/puppetlabs/puppet/puppet.conf"
    STAGE_FILE = "/etc/simple_grid/.stage"