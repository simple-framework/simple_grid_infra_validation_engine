import unittest
import testinfra


class TestCMInstall(unittest.TestCase):
    def setUp(self):
        self.host = testinfra.get_host("docker://basic_config_master")

    def test_vim_installed(self):
        self.host.package('vim').is_installed