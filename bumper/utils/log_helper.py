"""LogHelper module."""

import logging
import sys

import coloredlogs

from bumper.utils.settings import config as bumper_isc


class LogHelper:
    """LogHelper."""

    def __init__(self, logging_verbose: int = bumper_isc.bumper_verbose, logging_level: str = bumper_isc.bumper_level) -> None:
        self.update(logging_verbose=logging_verbose, logging_level=logging_level)

    def update(self, logging_verbose: int = bumper_isc.bumper_verbose, logging_level: str = bumper_isc.bumper_level) -> None:
        """Log Helper init."""
        # configure logger for requested verbosity
        log_format: str = "%(message)s"
        if logging_verbose >= 5:
            log_format = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)d :: %(message)s"
        elif logging_verbose == 4:
            log_format = (
                "[%(asctime)s,%(msecs)03d] :: %(levelname)-7s ::"
                " %(name)s[%(process)d] {%(lineno)-6d: (%(funcName)-30s)} - %(message)s"
            )
        elif logging_verbose == 3:
            log_format = (
                "[%(asctime)s] :: %(levelname)-5s ::"
                " [%(filename)-18s/%(module)-10s - %(lineno)-6d: (%(funcName)-30s)] - %(message)s"
            )
        elif logging_verbose == 2:
            log_format = "[%(asctime)s] %(levelname)-5s :: %(name)-22s - %(message)s"
        elif logging_verbose == 1:
            log_format = "[%(asctime)s] - %(message)s"

        # streamHandler = logging.StreamHandler(sys.stdout)
        # streamHandler.setFormatter(logging.Formatter(log_format))

        for logger_name in [logging.getLogger()] + [logging.getLogger(name) for name in logging.getLogger().manager.loggerDict]:
            for handler in logger_name.handlers:
                logger_name.removeHandler(handler)

            # # define new base stream handler and log level
            # logger_name.addHandler(streamHandler)
            # logger_name.setLevel(logging.getLevelName(logging_level))

            # add colored logs
            coloredlogs.install(
                level=logging.getLevelName(logging_level),
                fmt=log_format,
                logger=logger_name,
                stream=sys.stdout,
            )

            if logging_level == "INFO" and logger_name.name.startswith("aiohttp.access"):
                logger_name.setLevel(logging.DEBUG)
                logger_name.addFilter(AioHttpFilter())

            if logging_level == "INFO" and logger_name.name.startswith("httpx"):
                logger_name.setLevel(logging.WARNING)
            if logging_level == "INFO" and logger_name.name.startswith("amqtt"):
                logger_name.setLevel(logging.WARNING)


class AioHttpFilter(logging.Filter):
    """AioHttpFilter."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Aio Http Filter filter."""
        if record.name == "aiohttp.access" and record.levelno == 20:  # Filters aiohttp.access log to switch it from INFO to DEBUG
            record.levelno = 10
            record.levelname = "DEBUG"
        return bool(record.levelno == 10 and logging.getLogger("confserver").getEffectiveLevel() == 10)


logHelper = LogHelper()
