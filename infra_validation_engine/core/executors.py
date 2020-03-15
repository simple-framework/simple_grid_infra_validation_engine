import time
from infra_validation_engine.core import PipelineElement
from infra_validation_engine.core.concurrency import ThreadPool


class SerialExecutor(PipelineElement):
    """
    A wrapper around default behavior of PipelineElement that executes other PipelineElements serially.
    """
    def __init__(self, name):
        PipelineElement.__init__(self, name, "SerialExecutor")
        self.report['strategy'] = "serial"


class ParallelExecutor(PipelineElement):
    """
    A parallelized implementation for running a PipelineElement
    """

    def __init__(self, name, num_threads = 2, status_notification_interval=2):
        PipelineElement.__init__(self, name, "ParallelExecutor")
        self.pool = ThreadPool(num_threads)
        self.num_threads = num_threads
        self.status_notification_interval = status_notification_interval
        self.report["strategy"] = "parallel"

    def pre_condition(self):
        pass

    def run(self):
        """ Add n threads if the pipeline consists for n parallel executors to avoid a deadlock """
        total_elements = len(self.pipeline_elements)
        parallel_elements = [x for x in self.pipeline_elements if isinstance(x, ParallelExecutor)]
        num_parallel_elements = len(parallel_elements)
        num_threads = self.num_threads if num_parallel_elements > self.num_threads else num_parallel_elements
        # self.pool = ThreadPool(num_threads)

        for pipeline_element in self.pipeline_elements:
            self.pool.add_task(pipeline_element)

        """ Monitor Execution of tests"""
        while self.pool.infra_tests_q.qsize() > 0:
            self.logger.debug("{executor} queue status: {completed}/{total}".format(
                executor=self.name, total=total_elements,
                completed=(total_elements - self.pool.infra_tests_q.qsize())))
            time.sleep(self.status_notification_interval)
        self.pool.wait_completion()
