from logging import getLoggerClass, addLevelName, setLoggerClass, NOTSET
import logging

API_LOG_LEVEL = 5


class InfraValidationEngineLogger(getLoggerClass()):
    def __init__(self, name, level=NOTSET):
        super(InfraValidationEngineLogger, self).__init__(name, level)
        addLevelName(API_LOG_LEVEL, "API")

    def api(self, msg, *args, **kwargs):
        if self.isEnabledFor(API_LOG_LEVEL):
            self._log(API_LOG_LEVEL, msg, args, **kwargs)


logging.API = API_LOG_LEVEL
setLoggerClass(InfraValidationEngineLogger)