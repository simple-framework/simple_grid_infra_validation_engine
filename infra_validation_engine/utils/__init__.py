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

import infra_validation_engine
import logging


def get_lightweight_component_hosts(augmented_site_level_config):
    site_infrastructure = augmented_site_level_config['site_infrastructure']
    output = []
    for node in site_infrastructure:
        node['host'] = "ssh://{fqdn}".format(fqdn=node['fqdn'])
        output.append(node)
    return output


def config_root_logger(verbosity):
    """
    Configure application logger based on verbosity level received from CLI
    Verbosity values of 0, 1, 2 correspond to log level of Warning, Info, Debug respectively
    :param verbosity: integer: 0, 1, 2
    """
    root_logger = logging.getLogger(infra_validation_engine.__name__)
    if verbosity == 0:
        root_logger.setLevel(logging.WARNING)
    elif verbosity == 1:
        root_logger.setLevel(logging.INFO)
    elif verbosity >= 2:
        root_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  datefmt='%d/%m/%Y %I:%M:%S %p')
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)