class ComponentNotInstalledError(Exception):
    """ Raised when a framework component is not installed"""
    pass

class DirectoryNotFoundError(Exception):
    """Raised when a directory is excpected but not found"""
    pass

class FileNotCreatedError(Exception):
    """Raised when a file is excpected but not found"""
    pass

class FileContentsError(Exception):
    """Raised when a file contents differ from what is expected"""
    pass

class PackageNotInstalledError(Exception):
    """Raised when a package is expected but not installed"""
    pass
