"""LogHelper module."""

import copy
import logging
import sys
from typing import Any

import coloredlogs

from bumper.utils.settings import config as bumper_isc


class LogHelper:
    """Sets up and configures logging, including custom filters for various modules."""

    def __init__(self) -> None:
        """Initialize the logger with custom configuration based on verbosity."""
        logger_name_size = self._clean_logs()

        log_format: str = "%(message)s"
        if bumper_isc.bumper_verbose == 2:
            log_format = f"[%(asctime)s] %(levelname)-7s :: %(name)-{logger_name_size}s - %(message)s"
        elif bumper_isc.bumper_verbose == 1:
            log_format = "[%(asctime)s] - %(message)s"

        # Set root logger level
        root_logger = logging.getLogger("root")
        root_logger.setLevel(logging.getLevelName(bumper_isc.bumper_level))

        # Add the stream handler with log formatting
        root_handler = logging.StreamHandler(sys.stdout)
        root_handler.setFormatter(logging.Formatter(log_format))

        self._remove_existing_filter(root_handler, SanitizeFilter)
        root_handler.addFilter(SanitizeFilter())
        root_logger.addHandler(root_handler)

        # Use colored logs
        coloredlogs.install(
            level=logging.getLevelName(bumper_isc.bumper_level),
            fmt=log_format,
            logger=root_logger,
            stream=sys.stdout,
        )

    def _clean_logs(self) -> int:
        """Clean up existing logging handlers and applies custom settings based on module names."""
        logger_name_size = 0

        for logger_name in [logging.getLogger()] + [logging.getLogger(name) for name in logging.getLogger().manager.loggerDict]:
            logger_name_size = max(len(logger_name.name), logger_name_size)

            for handler in logger_name.handlers:
                logger_name.removeHandler(handler)

            if bumper_isc.bumper_level == "INFO" and (
                logger_name.name.startswith("httpx")
                or logger_name.name.startswith("transitions.core")
                or logger_name.name.startswith("amqtt")
            ):
                logger_name.setLevel(logging.WARNING)

            if logger_name.name.startswith("aiohttp.access") and bumper_isc.bumper_level == "INFO":
                logger_name.setLevel(logging.DEBUG)

            if logger_name.name.startswith("asyncio"):
                logger_name.addFilter(CertFilter())

        if aiohttp_access_logger := logging.getLogger("aiohttp.access"):
            aiohttp_access_logger.addFilter(AioHttpFilter())
        if amqtt_broker_logger := logging.getLogger("amqtt.broker"):
            amqtt_broker_logger.addFilter(AmqttFilter())

        return logger_name_size + 1

    def _remove_existing_filter(self, handler: logging.Handler, filter_cls: type[logging.Filter]) -> None:
        """Remove any existing instance of a specific filter from a handler."""
        for existing_filter in list(handler.filters):
            if isinstance(existing_filter, filter_cls):
                handler.removeFilter(existing_filter)


class AioHttpFilter(logging.Filter):
    """Filters aiohttp.access logs to adjust their level."""

    def filter(self, record: logging.LogRecord) -> bool:
        """AioHttpFilter filter."""
        if record.name == "aiohttp.access":
            return bool(logging.getLevelName(bumper_isc.bumper_level) == logging.getLevelName(logging.DEBUG))
        return True


class AmqttFilter(logging.Filter):
    """Filters amqtt log records to modify the level based on severity."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter amqtt log record."""
        if record.name == "amqtt.broker" and "No more data" in record.msg and record.levelno in (logging.WARNING, logging.ERROR):
            # NOTE: disabled this log on non DEBUG, as it spams when bot has cert pinning error
            return bool(logging.getLevelName(bumper_isc.bumper_level) == logging.getLevelName(logging.DEBUG))
        return True


class CertFilter(logging.Filter):
    """Filters SSL alert messages to suppress unnecessary warnings."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter SSL alert log record."""
        if record.exc_info and (
            "SSLV3_ALERT_CERTIFICATE_UNKNOWN" in str(record.args)
            or "SSLV3_ALERT_CERTIFICATE_UNKNOWN" in str(record.msg)
            or "SSLV3_ALERT_CERTIFICATE_UNKNOWN" in str(record.exc_info)
        ):
            record.msg = "SSLV3_ALERT_CERTIFICATE_UNKNOWN :: possible cert pinning"
            record.args = None
            record.exc_info = None
        return True


class SanitizeFilter(logging.Filter):
    """Sanitizes sensitive data from logs."""

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
        """Sanitize the log's args if they contain sensitive information."""
        if isinstance(record.args, dict):
            record.args = self._sanitize_data(record.args)
        elif isinstance(record.args, tuple):
            record.args = tuple(self._sanitize_data(value) for value in record.args)
        return True

    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize sensitive data in the provided structure."""
        if isinstance(data, list | set):
            return [self._sanitize_data(entry) for entry in data]

        # NOTE: do be done as it will remove everything and not only the secret when loop above for tuple
        if isinstance(data, str) and any(substring in data.lower() for substring in self._SANITIZE_LOG_KEYS):
            return "[REMOVED]"

        if isinstance(data, dict):
            sanitized_data = copy.deepcopy(data)
            for key, value in sanitized_data.items():
                if any(substring in key.lower() for substring in self._SANITIZE_LOG_KEYS):
                    sanitized_data[key] = "[REMOVED]"
                elif isinstance(value, dict | list | set):
                    sanitized_data[key] = self._sanitize_data(value)
            return sanitized_data

        return data
