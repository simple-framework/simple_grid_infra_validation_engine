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
import testinfra


class APIFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.API


def get_lightweight_component_hosts(augmented_site_level_config):
    """
    Prepares a list of host_representation objects for all LCs in site level config file
    :param augmented_site_level_config:
    :return: A list of testinfra_hosts for LC-hosts described in site level config file.
    """
    site_infrastructure = augmented_site_level_config['site_infrastructure']
    output = [get_host_representation(x['fqdn'], x['ip_address']) for x in site_infrastructure]
    return output


def add_testinfra_host(host_rep):
    host_rep['host'] = testinfra.get_host(host_rep['host_str'])


def get_host_representation(fqdn, ip_address=None):
    """
    Creates an object that contains information of the host on which tests will be run.
    :param fqdn: The fqdn of the machine. localhost in case of config master
    :param ip_address: The ip address of the machine. 127.0.0.1 in case of config master
    :return: A python dict
    {
        "fqdn": fqdn
        "ip_address": ip_address,
        "host": The testinfra connection for the machine
    }
    """
    host_str = fqdn if fqdn == "local://" else "ssh://{fqdn}".format(fqdn=fqdn)
    return {
        "fqdn": fqdn,
        "host_str": host_str,
        "ip_address": ip_address
    }


def config_root_logger(verbosity, mode):
    """
    Configure application logger based on verbosity level received from CLI
    Verbosity values of 0, 1, 2 correspond to log level of Warning, Info, Debug respectively
    :param verbosity: integer: 0, 1, 2
    """
    root_logger = logging.getLogger(infra_validation_engine.__name__)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  datefmt='%d/%m/%Y %I:%M:%S %p')
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if mode == 'standalone':
        if verbosity == 0:
            root_logger.setLevel(logging.WARNING)
        elif verbosity == 1:
            root_logger.setLevel(logging.INFO)
        elif verbosity >= 2:
            root_logger.setLevel(logging.DEBUG)
    elif mode == 'api':
        root_logger.setLevel(logging.API)
        console_handler.addFilter(APIFilter())