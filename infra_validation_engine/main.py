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

import sys
import yaml
import click
from infra_validation_engine.core import Pool
from stages.install import Install
from stages.test import Test
from utils import get_lightweight_component_hosts, get_host_representation, add_testinfra_host
import logging
from utils import config_root_logger
from __version__ import __version__

logger = logging.getLogger(__name__)


class Session:
    def __init__(self):
        self.config = {}

    def set_config(self, key, value):
        self.config[key] = value
        if self.verbose:
            logger.debug('  config[%s] = %s' % (key, value), file=sys.stderr)


pass_session = click.make_pass_decorator(Session)


@click.group()
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    ctx.obj = Session()


@cli.command()
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
              help="In API mode, output is JSON encoded. Default is standalone",
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
                type=click.Choice([x.lower() for x in Pool.get_all_stages()]),
                )
def validate(file, config_master, mode, verbose, targets, stages):
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
    exit_code = 1

    if targets is not None:
        hostnames = [x.strip() for x in targets.split(',')]
        lc_hosts_rep = [get_host_representation(x) for x in hostnames]
    else:
        logger.debug("No targets were explicitly specified to execute the tests. Using augmented_site_level_config "
                     "instead!")
        try:
            with open(file, 'r') as augmented_site_level_config_file:
                augmented_site_level_config = yaml.safe_load(augmented_site_level_config_file)
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

    if 'install' in stages:
        install_stage = Install(cm_host_rep, lc_hosts_rep)
        exit_code = install_stage.execute()
    elif 'test' in stages:
        test_stage = Test(cm_host_rep, lc_hosts_rep)
        exit_code = test_stage.execute()
    exit(exit_code)
    # logger.api( "test")
    # logger.api("test")


@cli.command()
def stages():
    """
    Lists all available stages
    """
    stages = Pool.get_all_stages()
    for stage in stages:
        click.echo("{stage}".format(stage=stage))


@cli.command()
# @click.option('--stage', '-s',
#               help="Filter tests by stages"
#               )
def tests():
    """
    Lists all available Infra Tests
    """
    tests = Pool.get_all_tests()
    for test in tests:
        click.echo("{test}".format(test=test))
