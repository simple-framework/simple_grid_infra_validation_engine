import sys
from abc import ABCMeta
import logging

from infra_validation_engine.core import Executor

IS_PY2 = sys.version_info < (3, 0)

if IS_PY2:
    from Queue import Queue
else:
    from queue import Queue

from threading import Thread

logger = logging.getLogger(__name__)


class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        logger.info("{worker}: Started \n".format(worker=self.name))
        while True:
            infra_test = self.tasks.get()
            logger.info("Queue status is {queue}".format(queue=self.tasks.qsize()))
            try:
                infra_test.execute()
                report = infra_test.report

                exit_code = infra_test.run()
                print "Running Test on {fqdn} exited {code}".format(fqdn=infra_test.fqdn, code=exit_code)
            except Exception as e:
                print "Error on {fqdn}".format(fqdn=infra_test.fqdn)
                # An exception happened in this thread
                print(e)
            finally:
                # Mark this task as done, whether an exception happened or not
                print "Removing Test for {fqdn}".format(fqdn=infra_test.fqdn)
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """

    def __init__(self, num_threads):
        self.infra_tests_q = Queue(num_threads)
        self.workers = []
        for _ in range(num_threads):
            self.workers.append(Worker(self.infra_tests_q))

    def add_task(self, infra_test):
        """ Add a task to the queue """
        print "Adding TEST FOR {fqdn} to QUEUE".format(fqdn=infra_test.fqdn)
        self.infra_tests_q.put(infra_test)
        print "Queue size: {queue}".format(queue=self.infra_tests_q.qsize())

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.infra_tests_q.join()


class ParallelExecutor(Executor):
    """
    Executes InfraTests in parallel.
    """
    __metaclass__ = ABCMeta

    def __init__(self, name, num_threads):
        Executor.__init__(self, name)
        self.num_threads = num_threads
        self.pool = ThreadPool(num_threads)

    def pre_condition(self):
        """ Ensure all tests are children of the Thread class """
        pass

    def execute(self):
        super(ParallelExecutor, self).execute()
        for test in self.infra_tests:
            self.pool.add_task(test)
        self.pool.wait_completion()
