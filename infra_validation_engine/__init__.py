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

from logging import getLoggerClass, addLevelName, setLoggerClass, NOTSET
import logging

API_LOG_LEVEL = 5


class InfraValidationEngineLogger(getLoggerClass()):
    """
    Overrides the default Logger class and adds the API log level
    """
    def __init__(self, name, level=NOTSET):
        super(InfraValidationEngineLogger, self).__init__(name, level)
        addLevelName(API_LOG_LEVEL, "API")

    def api(self, msg, *args, **kwargs):
        if self.isEnabledFor(API_LOG_LEVEL):
            self._log(API_LOG_LEVEL, msg, args, **kwargs)


logging.API = API_LOG_LEVEL
setLoggerClass(InfraValidationEngineLogger)