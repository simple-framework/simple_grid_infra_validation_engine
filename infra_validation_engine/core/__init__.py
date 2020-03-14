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
import json
import traceback
from abc import ABCMeta, abstractmethod
import logging
from infra_validation_engine.core.exceptions import DirectoryNotFoundError, PreConditionNotSatisfiedError
from collections import deque, OrderedDict


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
    """
    Exit_Code : 1,4,8::pass,pass+warn,error #someday
    """
    __metaclass__ = ABCMeta

    def __init__(self, name, description, host, fqdn):
        self.host = host
        self.name = name
        self.description = description
        self.fqdn = fqdn
        self.rc = -1
        self.err = None
        self.out = None
        # If message is specified, it will be present in report and output in api/standalone modes
        self.message = None
        self.warn = False
        self.logger = logging.getLogger(__name__)
        self.report = self.report = {'name': self.name, 'description': self.description, 'result': 'fail'}
        self.exit_code = 0

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def fail(self):
        pass

    def resolution(self):
        return ""

    def execute(self):
        log_str = "{test} on {fqdn}:".format(fqdn=self.fqdn, test=self.name)
        self.logger.info("{log_str} running".format(log_str=log_str))
        try:
            self.logger.info("{log_str} passed!".format(log_str=log_str))
            if self.run():  # test_passed
                # handle warnings
                if self.warn:
                    self.exit_code = 3
                    self.logger.warning("{log_str} {message}".format(log_str=log_str, message=self.message))
                self.report['result'] = 'pass'
            else:  # test failed
                try:
                    self.exit_code = 1
                    self.fail()
                except Exception as ex:
                    self.logger.error("{test} failed on {fqdn}! {details}".format(test=self.name,
                                                                                  fqdn=self.fqdn, details=ex.message))
                    self.logger.info("{log_str} {error} occurred!!".format(log_str=log_str, error=type(ex)),
                                     exc_info=True)
                    self.report["error"] = ex.message
                    self.report["trace"] = traceback.format_exc()
        except Exception as ex:
            self.exit_code = 1
            self.logger.error("{log_str} Could not run {test}!".format(log_str=log_str, test=self.name))
            self.logger.info(
                "{log_str} {error} occurred for {test}".format(log_str=log_str, test=self.name, error=type(ex)),
                exc_info=True)
            self.report["result"] = "exec_fail"
            self.report["error"] = ex.message
            self.report["trace"] = traceback.format_exc()
        if self.message is not None:
            self.logger.info(self.message)
            self.report['message'] = self.message

        # self.report['exit_code'] = self.exit_code


class Executor:
    """
    An abstract executor for InfraTests
    """
    __metaclass__ = ABCMeta

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(__name__)
        self.report = OrderedDict({"executor_name": self.name, "result": ''})
        self.infra_tests = []
        self.exit_code = 0
        self.hard_error_pre_condition = True

    def register_infra_test(self, infra_test):
        """ Register a test to be run by this executor """
        self.infra_tests.append(infra_test)

    @abstractmethod
    def pre_condition(self):
        """ Gather Info needed before running tests. Fail if the info is not available """
        pass

    @abstractmethod
    def run(self):
        """ Run the Tests """
        pass

    def execute(self):
        try:
            self.pre_condition()
        except PreConditionNotSatisfiedError as err:
            if self.hard_error_pre_condition:
                self.logger.error("The pre condition check for Executor {name} was not satisfied. "
                                  "Therefore, the execution of the following tests is being skipped: {tests}".format(
                                    name=self.name,
                                    tests=', '.join(
                                        ["{test} on {fqdn}".format(test=x.name, fqdn=x.fqdn) for x in self.infra_tests]
                                    )))
                self.report["result"] = "exec_fail"
                self.exit_code = 1
            else:
                self.logger.warning("The pre condition check for Executor {name} was not satisfied. "
                                    "However, we are continuing the execution of the tests")
                self.exit_code = 4 # pre_condition failed
            self.logger.info("Exception info: {error}".format(error=err.message), exc_info=True)
            self.report["error"] = err.message
            self.report["trace"] = traceback.format_exc()
            self.report["exit_code"] = self.exit_code

            if self.hard_error_pre_condition:
                return
        # Ready to run tests
        self.logger.info("Executing infrastructure tests for Executor {name}".format(name=self.name))
        test_name_csv = ', '.join([test.name for test in self.infra_tests])
        self.logger.info("Executor {name} has the following tests registered: {test_name_csv}".format(
            name=self.name,
            test_name_csv=test_name_csv))
        self.run()
        # Update report
        self.post_process()

    def post_process(self):
        """ Generate Report and update Exit Code """
        test_reports = [test.report for test in self.infra_tests]
        self.report['total_tests'] = len(test_reports)
        self.report['test_reports'] = test_reports
        exit_codes = set([test.exit_code for test in self.infra_tests])
        if self.exit_code == 4:
            self.report["result"] = "pre condition failed! "
        if 1 in exit_codes:
            self.exit_code = 1
            self.report["result"] += "some or all tests fail" #switch to codes someday
        elif 3 in exit_codes:
            self.exit_code = 3
            self.report["result"] += "warnings present"
        else:
            self.report["result"] += "all tests passed"

        # self.logger.api(json.dumps(self.report, indent=4))


class Stage:
    """ Serial executor of composition of SerialExecutors, ParallelExecutors"""

    __metaclass__ = ABCMeta

    def __init__(self, name, config_master_host, lightweight_component_hosts):
        self.name = name
        self.config_master_host = config_master_host
        self.lightweight_component_hosts = lightweight_component_hosts
        self.logger = logging.getLogger(__name__)
        self.executors = deque()
        self.create_test_pipeline()
        self.report = OrderedDict({"stage_name": self.name, "result": ''})
        self.hard_error_pre_condition = True
        self.exit_code = 0

    @abstractmethod
    def create_test_pipeline(self):
        pass

    @abstractmethod
    def pre_condition(self):
        pass

    def run(self):
        for executor in self.executors:
            executor.execute()

    def execute(self):
        try:
            self.pre_condition()
        except PreConditionNotSatisfiedError as err:
            if self.hard_error_pre_condition:
                self.logger.error("The pre condition check for Executor {name} was not satisfied. "
                                  "Therefore, the execution of the following tests is being skipped: {tests}".format(
                    name=self.name,
                    tests=', '.join(
                        ["{test} on {fqdn}".format(test=x.name, fqdn=x.fqdn) for x in self.infra_tests]
                    )))
                self.report["result"] = "exec_fail"
                self.exit_code = 1
            else:
                self.logger.warning("The pre condition check for Executor {name} was not satisfied. "
                                    "However, we are continuing the execution of the tests")
                self.exit_code = 4  # pre_condition failed
            self.logger.info("Exception info: {error}".format(error=err.message), exc_info=True)
            self.report["error"] = err.message
            self.report["trace"] = traceback.format_exc()
            self.report["exit_code"] = self.exit_code

            if self.hard_error_pre_condition:
                return

        # Ready to run tests
        self.logger.info("Executing Test Pipeline for Stage {name}".format(name=self.name))
        executor_name_csv = ', '.join([executor.name for executor in self.executors])
        self.logger.info("Stage {name} has the following executors registered: {executor_name_csv}".format(
            name=self.name,
            executor_name_csv=executor_name_csv))
        self.run()
        # Update report
        self.post_process()

    def post_process(self):
        """ Generate report and update exit code"""
        executor_reports = [executor.report for executor in self.executors]
        self.report['executor_reports'] = executor_reports
        self.report['total_executors'] = len(executor_reports)
        exit_codes = set([executor.exit_code for executor in self.executors])

        if self.exit_code == 4:
            self.report["result"] = "pre condition failed! "
        if 1 in exit_codes:
            self.exit_code = 1
            self.report["result"] += "some or all executors fail" #switch to codes someday
        elif 3 in exit_codes:
            self.exit_code = 3
            self.report["result"] += "warnings present"
        else:
            self.report["result"] += "all executors passed"

        self.logger.api(json.dumps(self.report, indent=4))


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
