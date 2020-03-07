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

import testinfra
import yaml
import click
from stages.install import Install
from utils import get_lightweight_component_hosts, get_host_representation, add_testinfra_host
import logging
from utils import config_root_logger

logger = logging.getLogger(__name__)


def execution_pipeline(config_master_host, lightweight_component_hosts, stages):
    if "install" in stages:
        install_stage = Install(config_master_host, lightweight_component_hosts)
        install_stage.execute()


@click.command()
@click.option('--file', '-f',
              default='/etc/simple_grid/site_config/augmented_site_level_config_file.yaml',
              type=click.STRING,
              required=False,
              help="The absolute path to the augmented_site_level_config_file.yaml. "
                   "Default is /etc/simple_grid/site_config/augmented_site_level_config_file.yaml"
              )
@click.option('--config-master', '-c',
              default='local://',
              help='FQDN of the Config Master node. Default is localhost.')
@click.option('--mode', '-m',
              type=click.Choice(['api', 'standalone'], case_sensitive=False),
              help="In API mode, exit codes are non zero in case of failures. Default is standalone",
              default='standalone')
@click.option('--verbose', '-v',
              count=True,
              help="Set verbosity level. Select between -v, -vv or -vvv.")
@click.option('--targets', '-t',
              type=click.STRING,
              help="A comma separated list of FQDNs of the Lightweight Component hosts whose state should be validated"
                   "If --file is specified as well, tests are executed only on --targets ")
@click.argument('stages',
                nargs=-1,
                type=click.Choice(['install', 'config', 'pre_deploy', 'deploy']),
                )
def cli(file, config_master, mode, verbose, targets, stages):
    """
    Execute the infra validation engine for the SIMPLE Framework and validate the configuration of CM and LC hosts stage
    by stage.
    """
    config_root_logger(verbose, mode)

    logger.debug("config_master: {cm}".format(cm=config_master))
    logger.debug("verbosity: {val}".format(val=verbose))
    logger.debug("mode: {val}".format(val=mode))
    logger.debug("targets: {val}".format(val=targets))
    logger.debug("stages: {val}".format(val=stages))

    cm_host_rep = get_host_representation(config_master, '0.0.0.0')
    lc_hosts_rep = []
    all_hosts_rep = [cm_host_rep]
    augmented_site_level_config = None

    if targets is not None:
        hostnames = [x.strip() for x in targets.split(',')]
        lc_hosts_rep = [get_host_representation(x) for x in hostnames]
    else:
        logger.debug("No targets were explicitly specified to execute the tests. Using augmented_site_level_config "
                     "instead!")
        if file is None:
            logger.warning("No --targets specified and no --file specified. Tests will only run on the Config Master")
        else:
            try:
                with open(file, 'r') as augmented_site_level_config_file:
                    augmented_site_level_config = yaml.safe_load(f)
            except IOError:
                logger.info("Could not read augmented site level config file")
                logger.debug("Exception:", exc_info=True)

        if augmented_site_level_config is not None:
            lc_hosts_rep = get_lightweight_component_hosts(augmented_site_level_config)

    if len(lc_hosts_rep) == 0:
        logger.info("No LC hosts specified through --targets or --file")
    else:
        all_hosts_rep.extend(lc_hosts_rep)

    logger.info("Infra Validation Tests will be executed on the following hosts:")
    map(lambda x: logger.info(x['fqdn']), all_hosts_rep)

    add_testinfra_host(cm_host_rep)
    for host_rep in all_hosts_rep[1:]:
        add_testinfra_host(host_rep)
    # logger.api( "test")
    logger.api("test")


if __name__ == "__main__":
    args = parse_args()
    site_level_config_file = args['filename']
    config_master_host = args['config_master_host']
    stages = args['stages'].split(',')
    if config_master_host is not None:
        config_master_host = testinfra.get_host(config_master_host)
    else:
        config_master_host = testinfra.get_host('local://')

    config_master_host = {
        'fqdn': 'localhost',
        'host': config_master_host,
        'ip_address': '127.0.0.1'
    }

    # output = test_cm_git_install(config_master_host['host'])

    augmented_site_level_config = yaml.safe_load(open('./.temp/augmented_site_level_config_file.yaml', 'r'))
    lc_hosts = get_lightweight_component_hosts(augmented_site_level_config)

    print(lc_hosts)
    for lc_host in lc_hosts:
        lc_host['host'] = testinfra.get_host(lc_host['host'])
        git_test = test_cm_git_install(lc_host['host'])
        print "Git Test on {fqdn}: {git_test}".format(fqdn=lc_host['fqdn'], git_test=git_test)
    execution_pipeline(config_master_host, lc_hosts, stages)