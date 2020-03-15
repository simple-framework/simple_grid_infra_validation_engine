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
import itertools
import socket

import yaml

from infra_validation_engine.core import Stage, StageType
from infra_validation_engine.core.exceptions import PreConditionNotSatisfiedError
from infra_validation_engine.core.executors import ParallelExecutor, SerialExecutor
from infra_validation_engine.core.standard_tests import PingTest, SSHTest, FileIsPresentTest
from infra_validation_engine.infra_tests.components.puppet import PuppetAgentInstallationTest, PuppetServiceTest, \
    PuppetServerInstallationTest, PuppetModuleTest
from infra_validation_engine.utils.constants import ComponentRepositoryConstants


class PasswordlessSSHChecker(ParallelExecutor):
    """ Check if CM can SSH as root to all LCs (passwordless)"""

    def __init__(self, cm_rep, lc_rep, key, num_threads):
        ParallelExecutor.__init__(self, "Passwordless SSH Validator", num_threads)
        self.host = cm_rep['host']
        self.fqdn = cm_rep['fqdn']
        self.lc_rep = lc_rep
        self.key = key
        self.create_pipeline()

    def create_pipeline(self):
        for lc in self.lc_rep:
            self.append_to_pipeline(SSHTest("SSH root@{dest}".format(src=self.fqdn, dest=lc['fqdn']),
                                            lc['fqdn'],
                                            "SSH {src} to root@{dest}".format(src=self.fqdn, dest=lc['fqdn']),
                                            self.host,
                                            self.fqdn,
                                            key=self.key
                                            ))


class ClusterWideDNSChecker(ParallelExecutor):

    def __init__(self, cm_rep, lc_rep, num_threads):
        ParallelExecutor.__init__(self, "DNS Config Validator", num_threads)
        self.cm_rep = cm_rep
        self.cm_rep['fqdn'] = socket.getfqdn()
        self.lc_rep = lc_rep
        self.node_rep = [cm_rep] + lc_rep
        self.node_permutation = itertools.permutations(self.node_rep, 2)
        self.create_pipeline()

    def create_pipeline(self):
        for node_pair in self.node_permutation:
            self.append_to_pipeline(
                PingTest("Ping {dest} from {src}".format(dest=node_pair[1]['fqdn'], src=node_pair[0]['fqdn']),
                         node_pair[1]['fqdn'],
                         "Ping test for {dest} from {src}".format(dest=node_pair[1]['fqdn'], src=node_pair[0]['fqdn']),
                         node_pair[0]['host'],
                         node_pair[0]['fqdn']
                         )
            )


class NetworkValidator(SerialExecutor):

    def __init__(self, cm_rep, lc_rep, key, num_threads):
        SerialExecutor.__init__(self, "Network Validator")
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.key = key
        self.num_threads = num_threads
        self.create_pipeline()

    def create_pipeline(self):
        self.extend_pipeline([
            ClusterWideDNSChecker(self.cm_rep, self.lc_rep, self.num_threads),
            PasswordlessSSHChecker(self.cm_rep, self.lc_rep, self.key, self.num_threads)
        ])


class PuppetValidator(ParallelExecutor):

    def __init__(self, cm_rep, lc_rep, num_threads):
        ParallelExecutor.__init__(self, "Puppet and Puppet Module Validator", num_threads)
        self.all_hosts = [cm_rep] + lc_rep
        self.num_threads = num_threads
        self.create_pipeline()

    def create_pipeline(self):
        for node in self.all_hosts:
            self.extend_pipeline([
                PuppetAgentInstallationTest(node['host'], node['fqdn']),
                PuppetServiceTest(node['host'], node['fqdn']),
                PuppetModuleTest(node['host'], node['fqdn'])
            ])


class PreInstallParallelExecutor(ParallelExecutor):
    """
    Stage is serial executor by default, we need to insert a parallel
    executor for pre_install given the nature of tests
    """

    def __init__(self, cm_rep, lc_rep, key, num_threads, host_cert_dirs, hooks):
        ParallelExecutor.__init__(self, " Pre Install Parallelizer", num_threads)
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.host = cm_rep['host']
        self.fqdn = cm_rep['fqdn']
        self.key = key
        self.num_threads = num_threads
        self.host_cert_dirs = host_cert_dirs
        self.hooks = hooks
        self.create_pipeline()

    def create_pipeline(self):
        self.extend_pipeline([
            NetworkValidator(self.cm_rep, self.lc_rep, self.key, self.num_threads),
            PuppetValidator(self.cm_rep, self.lc_rep, self.num_threads),
            PuppetServerInstallationTest(self.host, self.fqdn),
            FileIsPresentTest("Site Level Config File Test",
                              "{site_config}".format(site_config=ComponentRepositoryConstants.SITE_LEVEL_CONFIG_FILE),
                              self.host,
                              self.fqdn)
        ])
        for cert_dir in self.host_cert_dirs:
            self.extend_pipeline([
                FileIsPresentTest("Host Certificate Test: {dir}".format(dir=cert_dir),
                                  "{dir}/hostcert.pem".format(dir=cert_dir),
                                  self.host,
                                  self.fqdn
                                  ),
                FileIsPresentTest("Host Certificate Test: {dir}".format(dir=cert_dir),
                                  "{dir}/hostkey.pem".format(dir=cert_dir),
                                  self.host,
                                  self.fqdn
                                  )
            ])
        for hook in self.hooks:
            self.append_to_pipeline(
                FileIsPresentTest("Lifecycle Hook Test: {path}".format(path=hook),
                                  hook,
                                  self.host,
                                  self.fqdn
                                  )
            )


class Pre_Install(Stage):
    __metaclass__ = StageType

    def __init__(self, cm_rep, lc_rep, augmented_site_level_config_file, key, num_threads):
        Stage.__init__(self, "Pre_Install")
        self.cm_rep = cm_rep
        self.lc_rep = lc_rep
        self.key = key
        self.num_threads = num_threads
        self.augmented_site_level_config_file = augmented_site_level_config_file
        self.augmented_site_level_config = None
        self.host_cert_dirs = []
        self.hooks = []

    def pre_condition(self):
        try:
            with open(self.augmented_site_level_config_file, 'r') as augmented_site_level_config_file:
                self.augmented_site_level_config = yaml.safe_load(augmented_site_level_config_file)
        except Exception:
            raise PreConditionNotSatisfiedError("Could not read augmented site level config file from {path}"
                                                .format(path=self.augmented_site_level_config_file))
        self.create_pipeline()

    def create_pipeline(self):
        self.parse_augmented_site_config()
        self.append_to_pipeline(PreInstallParallelExecutor(self.cm_rep, self.lc_rep,
                                                           self.key, self.num_threads,
                                                           self.host_cert_dirs, self.hooks))

    def parse_augmented_site_config(self):
        lcs = self.augmented_site_level_config['lightweight_components']
        for lc in lcs:
            name = lc['name'].lower()
            fqdn = lc['deploy']['node']
            meta_info_header = "{prefix}{name}".format(
                prefix=ComponentRepositoryConstants.META_INFO_PREFIX,
                name=name
            )
            if meta_info_header in self.augmented_site_level_config:
                meta_info = self.augmented_site_level_config[meta_info_header]
                if "host_requirements" in meta_info:
                    host_requirements = meta_info["host_requirements"]
                    if "host_certificates" in host_requirements:
                        if host_requirements['host_certificates'] is True:
                            self.host_cert_dirs.append("{host_cert_dir}/{fqdn}"
                                                       .format(host_cert_dir=ComponentRepositoryConstants.HOST_CERT_DIR,
                                                               fqdn=fqdn))
            if "lifecycle_hooks" in lc:
                hooks = lc['lifecycle_hooks']
                if "pre_config" in hooks:
                    self.hooks.extend(hooks['pre_config'])
                if "pre_init" in hooks:
                    self.hooks.extend(hooks['pre_init'])
                if "post_init" in hooks:
                    self.hooks.extend(hooks['post_init'])
