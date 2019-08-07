from abc import ABCMeta, abstractmethod


class InfraTest:
    __metaclass__ = ABCMeta

    def __init__(self, host):
        self.host = host

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def fail(self):
        pass
