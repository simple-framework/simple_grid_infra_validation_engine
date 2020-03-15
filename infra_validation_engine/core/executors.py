import logging
import time
from abc import abstractmethod, ABCMeta
from collections import OrderedDict

from infra_validation_engine.core import Executor, PreConditionNotSatisfiedError, InfraTest
from infra_validation_engine.core.concurrency import ThreadPool


class Pipeline:
    """
    An executor of executors
    """
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(__name__)
        self.report = OrderedDict({"pipeline_name": self.name, "result": ''})
        self.executors = []
        self.exit_code = 0
        self.hard_error_pre_condition = True

    def pre_condition(self):
        pass


class HorizontalExecutor(Executor):
    """
    Composed of Serial Executors, Parallel Executors and InfraTests. The pipeline is executed serially.
    """
    def __init__(self, name):
        Executor.__init__(self, name)
        self.report['executor_type'] = "horizontal"
    def pre_condition(self):
        pass

    def run(self):
        for pipeline_element in self.pipeline:
            pipeline_element.execute()


class VerticalExecutor(Executor):
    """
    Composed of Serial Executors, Parallel Executors and InfraTests. The pipeline is executed serially.
    """

    def __init__(self, name, num_threads = 2, status_notification_interval=2):
        Executor.__init__(self, name)
        self.pool = ThreadPool(num_threads)
        self.num_threads = num_threads
        self.status_notification_interval = status_notification_interval
        self.report["executor_type"] = "vertical"

    def pre_condition(self):
        pass

    def run(self):
        """ Add n threads if the pipeline consists for n parallel executors to avoid a deadlock """
        total_elements = len(self.pipeline)
        parallel_elements = [x for x in self.pipeline if isinstance(x, VerticalExecutor)]
        num_parallel_elements = len(parallel_elements)
        num_threads = self.num_threads if num_parallel_elements > self.num_threads else num_parallel_elements
        # self.pool = ThreadPool(num_threads)

        for pipeline_element in self.pipeline:
            self.pool.add_task(pipeline_element)

        """ Monitor Execution of tests"""
        while self.pool.infra_tests_q.qsize() > 0:
            self.logger.debug("{executor} queue status: {completed}/{total}".format(
                executor=self.name, total=total_elements,
                completed=(total_elements - self.pool.infra_tests_q.qsize())))
            time.sleep(self.status_notification_interval)
        self.pool.wait_completion()


class SerialExecutor(Executor):
    """
    Collection and Execution of InfraTests. Tests are serially connected i.e. if one test passes,
    then we move to the next test. If a test fails, the pipeline reports the error, warning.
    """
    __metaclass__ = ABCMeta

    def __init__(self, name):
        Executor.__init__(self, name)

    @abstractmethod
    def pre_condition(self):
        pass

    def run(self):
        for infra_test in self.infra_tests:
            infra_test.execute()


class ParallelExecutor(Executor):
    """
    Executes InfraTests in parallel.
    """
    __metaclass__ = ABCMeta

    def __init__(self, name, num_threads=10, status_notification_interval=2):
        Executor.__init__(self, name)
        self.num_threads = num_threads
        self.pool = ThreadPool(num_threads)
        self.status_notification_interval = status_notification_interval
        self.report["executor_type"] = "parallel"

    def pre_condition(self):
        """ Ensure all tests are children of the Thread class """
        pass

    def run(self):
        """ Execute tests in parallel """
        total_tests = len(self.infra_tests)
        for test in self.infra_tests:
            self.pool.add_task(test)

        """ Monitor Execution of tests"""
        while self.pool.infra_tests_q.qsize() > 0:
            self.logger.debug("{executor} queue status: {completed}/{total}".format(
                executor=self.name, total=total_tests,
                completed=(total_tests - self.pool.infra_tests_q.qsize())))
            time.sleep(self.status_notification_interval)
        self.pool.wait_completion()
