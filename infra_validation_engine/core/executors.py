import time
from abc import abstractmethod, ABCMeta
from infra_validation_engine.core import Executor
from infra_validation_engine.core.concurrency import ThreadPool


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
        super(SerialExecutor, self).run()
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
        super(ParallelExecutor, self).run()
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
