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

from abc import ABCMeta, abstractmethod
import logging
import sys


class Pool:
    """
    Manages a list of all available infra tests and the stages
    """
    tests = []
    stages = []
    logger = logging.getLogger(__name__)

    @staticmethod
    def register_test(name):
        Pool.tests.append(name)
        Pool.logger.debug("Registered {test} in test pool".format(test=name))

    @staticmethod
    def register_stage(name):
        Pool.stages.append(name)
        Pool.logger.debug("Registered {stage} in test pool".format(stage=name))

    @staticmethod
    def get_all_tests():
        return Pool.tests

    @staticmethod
    def get_all_stages():
        return Pool.stages


class InfraTest:
    __metaclass__ = ABCMeta

    def __init__(self, name, description, host, fqdn):
        self.host = host
        self.name = name
        self.description = description
        self.fqdn = fqdn

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def fail(self):
        pass


class Stage:
    """ Collection and Execution of InfraTests """

    __metaclass__ = ABCMeta

    def __init__(self, name, config_master_host, lightweight_component_hosts):
        self.name = name
        self.infra_tests = list()
        self.config_master_host = config_master_host
        self.lightweight_component_hosts = lightweight_component_hosts
        self.logger = logging.getLogger("{stage}-{name}".format(stage=Stage.__name__, name=self.name))
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler(stream=sys.stdout))
        self.register_tests()

    @abstractmethod
    def register_tests(self):
        pass

    def execute(self):
        self.logger.info("Execution infrastructure tests for {stage}".format(stage=self.name))
        test_name_csv = ', '.join([test.name for test in self.infra_tests])
        self.logger.info("Stage {stage} has the following tests registered: {test_name_csv}".format(stage=self.name,
                                                                                                   test_name_csv=test_name_csv))
        for test in self.infra_tests:
            self.logger.info("Running {test_name} on {node}".format(test_name=test.name, node=test.fqdn))
            if test.run():
                self.logger.info("{test} passed!".format(test=test.name))
            else:
                try:
                    test.fail()
                except Exception as ex:
                    self.logger.exception("{test} failed".format(test=test.name), exc_info=True)


class StageType(ABCMeta):
    """
    Automatically register a class that has __metaclass__ = StageType in the Pool
    see: https://stackoverflow.com/a/100146
    """
    logger = logging.getLogger(__name__)

    def __init__(cls, name, bases, attrs):
        super(StageType, cls).__init__(name, bases, attrs)
        Pool.register_stage(name)
        StageType.logger.debug("Registering Stage {name}".format(name=name))


class InfraTestType(ABCMeta):
    """
    Automatically register a class with __metaclass__ = TestType in the Pool
    see: https://stackoverflow.com/a/100146
    """
    logger = logging.getLogger(__name__)

    def __init__(cls, name, bases, attrs):
        super(InfraTestType, cls).__init__(name, bases, attrs)
        Pool.register_test(name)
        StageType.logger.debug("Registering Test {name}".format(name=name))