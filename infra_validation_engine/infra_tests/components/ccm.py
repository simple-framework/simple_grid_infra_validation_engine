from infra_validation_engine.core import InfraTest, InfraTestType
from infra_validation_engine.utils.constants import Constants
from infra_validation_engine.core.standard_tests import DirectoryIsPresentTest, FileIsPresentTest


class SimpleConfDirTest(DirectoryIsPresentTest):
    """SIMPLE Conf directory is present Test"""
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        DirectoryIsPresentTest.__init__(self, "SIMPLE Conf directory Test", Constants.SIMPLE_CONFIG_DIR, host, fqdn)


class AugSiteConfTest(FileIsPresentTest):
    """Augmented Site-level config file is present Test"""
    __metaclass__ = InfraTestType

    def __init__(self, host, fqdn):
        FileIsPresentTest.__init__(self, "Augmented Site-level config file Test", Constants.SITE_LEVEL_CONFIG_FILE, host, fqdn)