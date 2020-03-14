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


class ComponentNotInstalledError(Exception):
    """ Raised when a framework component is not installed"""
    pass


class DirectoryNotFoundError(Exception):
    """Raised when a directory is expected but not found"""
    pass


class FileNotFoundError(Exception):
    """Raised when a file is expected but not found"""
    pass


class FileContentsMismatchError(Exception):
    """Raised when a file contents differ from what is expected"""
    pass

  
class PackageNotFoundError(Exception):
    """Raised when a package is expected but not installed"""
    pass


class PackageNotConfiguredError(Exception):
    """Raised if the configuration of package is improper or not found"""
    pass


class NetworkError(Exception):
    """Raised if nodes cannot connect to each other"""
    pass


class ServiceNotRunningError(Exception):
    """Raised if service is not running on the host"""
    pass


class ServiceNotFoundError(Exception):
    """Raised if service is not found on the host"""
    pass


class CommandExecutionError(Exception):
    """ Raised if a command could not be executed on a node """
    pass


class PreConditionNotSatisfiedError(Exception):
    """ Raised if a pre condition for an Executor fails"""
