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
    """Raised when a directory is excpected but not found"""
    pass


class FileNotCreatedError(Exception):
    """Raised when a file is excpected but not found"""
    pass


class FileContentsMismatchError(Exception):
    """Raised when a file contents differ from what is expected"""
    pass

  
class PackageNotInstalledError(Exception):
    """Raised when a package is expected but not installed"""
    pass
