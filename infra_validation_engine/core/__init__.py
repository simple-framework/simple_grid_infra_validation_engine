from abc import ABCMeta, abstractmethod
import logging
import sys


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
