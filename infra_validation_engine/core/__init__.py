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


class PipelineElement:
    """ Pipeline elements that can be executed """
    __metaclass__ = ABCMeta

    def __init__(self, name, executable_type):
        self.name = name
        self.type = executable_type #InfraTest, Executor, Stage, HorizontalExecutor, VerticalExecutor
        self.pipeline_elements = []
        self.exit_code = 0
        self.report = OrderedDict({'name': self.name, 'result': '', 'type': self.type})
        self.logger = logging.getLogger(__name__)
        self.hard_error_pre_condition = True

    def append_to_pipeline(self, pipeline_element):
        self.pipeline_elements.append(pipeline_element)

    def extend_pipeline(self, pipeline_elements):
        for pipeline_element in pipeline_elements:
            self.append_to_pipeline(pipeline_element)

    def pre_condition(self):
        """
        Override if certain checks need to be performed before executing the pipeline.
        Copy artifacts etc.
        """
        pass

    def pre_condition_handler(self):
        return_status = False
        try:
            self.pre_condition()
            return_status = True
        except PreConditionNotSatisfiedError as err:
            if self.hard_error_pre_condition:
                self.logger.error("The pre condition check for {type} {name} was not satisfied. "
                                  "Therefore, the execution of the following pipeline elements is "
                                  "being skipped: {elements}".format(
                    name=self.name,
                    type=self.type,
                    elements=', '.join(
                        ["{element}".format(element=element) for element in self.pipeline_elements]
                    )))
                self.report["result"] = "exec_fail"
                self.exit_code = 1
            else:
                self.logger.warning("The pre condition check for {type} {name} was not satisfied. "
                                    "However, we are continuing the execution of the tests".
                                    format(name=self.name,type=self.type))
                self.exit_code = 4  # pre_condition failed
                return_status = True
            self.logger.info("Exception info: {error}".format(error=err.message), exc_info=True)
            self.report["error"] = err.message
            self.report["trace"] = traceback.format_exc()
            self.report["exit_code"] = self.exit_code

        return return_status

    def run(self):
        for element in self.pipeline_elements:
            element.execute()

    def execute(self):
        if not self.pre_condition_handler():
            self.logger.error("Pre condition failed for {type}: {name}".format(name=self.name, type=self.type))
            return
        self.logger.info("Executing Pipeline for {type} {name}".format(name=self.name, type=self.type))
        pipeline_elements_csv = ', '.join([element.name for element in self.pipeline_elements])
        self.logger.info("{type} {name} has the following pipeline elements registered: {pipeline_elements}".format(
            name=self.name,
            type=self.type,
            pipeline_elements=pipeline_elements_csv))
        self.run()
        # Update report
        self.post_process()

    def post_process(self):
        """ Generate Report and update Exit Code """
        pipeline_reports = [element.report for element in self.pipeline_elements]
        self.report['total_elements'] = len(pipeline_reports)
        self.report['element_reports'] = pipeline_reports
        exit_codes = set([test.exit_code for test in self.pipeline_elements])
        if self.exit_code == 4:
            self.report["result"] = "pre condition failed! "
        if 1 in exit_codes:
            self.exit_code = 1
            self.report["result"] += "some or all tests fail"  # switch to codes someday
        elif 3 in exit_codes:
            self.exit_code = 3
            self.report["result"] += "warnings present"
        else:
            self.report["result"] += "all tests passed"


class InfraTest(PipelineElement):
    """
    Exit_Code : 1,4,8::pass,pass+warn,error #someday
    """
    __metaclass__ = ABCMeta

    def __init__(self, name, description, host, fqdn):
        PipelineElement.__init__(self, name, "InfraTest")
        self.description = description
        self.host = host
        self.fqdn = fqdn
        self.rc = -1
        self.err = None
        self.out = None
        # If message is specified, it will be present in report and output in api/standalone modes
        self.message = None
        self.warn = False
        self.report['description'] = self.description
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


class Stage(PipelineElement):
    """ Serial executor of composition of SerialExecutors, ParallelExecutors"""

    __metaclass__ = ABCMeta

    def __init__(self, name, config_master_host, lightweight_component_hosts):
        PipelineElement.__init__(self, name, "Stage")
        self.name = name
        self.config_master_host = config_master_host
        self.lightweight_component_hosts = lightweight_component_hosts
        self.hard_error_pre_condition = True
        self.create_pipeline()

    @abstractmethod
    def create_pipeline(self):
        pass

    def post_process(self):
        """ Generate report and update exit code"""
        super(Stage, self).post_process()
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
