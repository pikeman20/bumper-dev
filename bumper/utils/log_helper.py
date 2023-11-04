"""LogHelper module."""

import copy
import logging
import sys
from typing import Any

import coloredlogs

from bumper.utils.settings import config as bumper_isc


class LogHelper:
    """LogHelper."""

    def __init__(self, logging_verbose: int = bumper_isc.bumper_verbose, logging_level: str = bumper_isc.bumper_level) -> None:
        """Log Helper init."""
        logger_name_size = self._clean_logs()
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
            log_format = f"[%(asctime)s] %(levelname)-5s :: %(name)-{logger_name_size}s - %(message)s"
        elif logging_verbose == 1:
            log_format = "[%(asctime)s] - %(message)s"

        self._clean_logs(logging_level)
        root_logger = logging.getLogger("root")

        root_handler = logging.StreamHandler(sys.stdout)
        root_handler.setFormatter(logging.Formatter(log_format))
        root_handler.addFilter(SanitizeFilter())

        # root_logger.addHandler(root_handler)
        # root_logger.setLevel(logging.getLevelName(logging_level))

        # add colored logs
        coloredlogs.install(
            level=logging.getLevelName(logging_level),
            fmt=log_format,
            logger=root_logger,
            stream=sys.stdout,
        )

    def _clean_logs(self, logging_level: str = bumper_isc.bumper_level) -> int:
        logger_name_size = 4
        for logger_name in [logging.getLogger()] + [logging.getLogger(name) for name in logging.getLogger().manager.loggerDict]:
            for handler in logger_name.handlers:
                logger_name.removeHandler(handler)
            # for filter in logger_name.filters:
            #     logger_name.removeFilter(filter)

            if logging_level == "INFO" and logger_name.name.startswith("aiohttp.access"):
                logger_name.setLevel(logging.DEBUG)
                logger_name.addFilter(AioHttpFilter())

            if logging_level == "INFO" and logger_name.name.startswith("httpx"):
                logger_name.setLevel(logging.WARNING)
            if logging_level == "INFO" and logger_name.name.startswith("amqtt"):
                logger_name.setLevel(logging.WARNING)
            if (logger_name_size := len(logger_name.name)) >= logger_name_size:
                pass
        return logger_name_size + 1


class AioHttpFilter(logging.Filter):
    """AioHttpFilter."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Aio Http Filter filter."""
        if record.name == "aiohttp.access" and record.levelno == 20:  # Filters aiohttp.access log to switch it from INFO to DEBUG
            record.levelno = 10
            record.levelname = "DEBUG"
        return bool(record.levelno == 10 and logging.getLogger("confserver").getEffectiveLevel() == 10)


class SanitizeFilter(logging.Filter):
    """Filter to sensitive data."""

    # all lowercase
    _SANITIZE_LOG_KEYS: set[str] = {
        "auth",
        "did",
        "email",
        "login",
        "mobile",
        "token",
        "uid",
        "user",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record."""
        # The call signature matches string interpolation: args can be a tuple or a dict
        if isinstance(record.args, dict):
            record.args = self._sanitize_data(record.args)
        elif isinstance(record.args, tuple):
            record.args = tuple(self._sanitize_data(value) for value in record.args)

        return True

    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize data (remove personal data)."""
        if isinstance(data, (set, list)):
            return [self._sanitize_data(entry) for entry in data]

        if not isinstance(data, dict):
            return data

        sanitized_data = None
        for key, value in data.items():
            if any(substring in key.lower() for substring in self._SANITIZE_LOG_KEYS):
                if sanitized_data is None:
                    sanitized_data = copy.deepcopy(data)
                sanitized_data[key] = "[REMOVED]"
            elif isinstance(value, (set, list, dict)):
                if sanitized_data is None:
                    sanitized_data = copy.deepcopy(data)
                sanitized_data[key] = self._sanitize_data(value)

        return sanitized_data if sanitized_data else data
