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
import logging


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
        logger.debug("{worker}: Started \n".format(worker=self.name))
        while True:
            pipeline_element = self.tasks.get()
            # infra_test = self.tasks.get()
            pipeline_element.report["executor_thread"] = self.name
            try:
                pipeline_element.execute()
            except Exception as e:
                # An exception happened in this thread
                err_msg = "Error during parallel execution of {element}".format(element=pipeline_element.name)
                logger.error("{worker}: {err_msg}".format(worker=self.name, err_msg=err_msg))
                logger.debug("{worker}: {error} occurred when executing {element}".format(worker=self.name,
                                                                                          error=type(e),
                                                                                          element=pipeline_element.name,
                                                                                          ), exc_info=True)
            finally:
                # Mark this task as done, whether an exception happened or not
                logger.debug("{worker}: Dequeue {element}. Test exit code was: {code}".format(
                    worker=self.name,
                    element=pipeline_element.name,
                    code=pipeline_element.exit_code))
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """

    def __init__(self, num_threads):
        self.infra_tests_q = Queue(num_threads)
        self.workers = []
        for _ in range(num_threads):
            self.workers.append(Worker(self.infra_tests_q))

    def add_worker(self):
        self.workers.append(Worker(self.infra_tests_q))

    def add_task(self, infra_test):
        """ Add a task to the queue """
        logger.debug("Queueing {task}".format(task=infra_test.name))
        self.infra_tests_q.put(infra_test)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.infra_tests_q.join()


