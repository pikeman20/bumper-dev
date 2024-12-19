import logging

import pytest

from bumper.utils.log_helper import AioHttpFilter, LogHelper, SanitizeFilter


@pytest.mark.parametrize("level", ["INFO"])
def test_log_helper_init(log_helper, caplog: pytest.LogCaptureFixture) -> None:
    assert isinstance(log_helper, LogHelper)

    # Check that log level is set correctly
    assert logging.getLogger("root").getEffectiveLevel() == logging.getLevelName("INFO")

    # Ensure that SanitizeFilter is added to the root handler
    for handler in logging.getLogger("root").handlers:
        if len(handler.filters) > 0:
            assert isinstance(handler.filters[0], SanitizeFilter)

    # Check that AioHttpFilter is added to the aiohttp.access logger
    aiohttp_access_logger = logging.getLogger("aiohttp.access")
    assert isinstance(aiohttp_access_logger.filters[0], AioHttpFilter)

    # Test log message
    logging.getLogger().info("Test log message")
    assert "Test log message" in caplog.text


def test_log_helper_clean_logs() -> None:
    logger_name_size = LogHelper()._clean_logs()
    assert logger_name_size > 0


@pytest.mark.parametrize("level", ["DEBUG"])
def test_aiohttp_filter(log_helper) -> None:
    aiohttp_filter = AioHttpFilter()

    # Test that it switches INFO to DEBUG
    record = logging.LogRecord(
        name="aiohttp.access",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="",
        args=None,
        exc_info=None,
    )
    assert aiohttp_filter.filter(record)
    assert record.levelno == logging.DEBUG

    # Test that it doesn't change other log levels
    record = logging.LogRecord(
        name="some_other_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="",
        args=None,
        exc_info=None,
    )
    assert not aiohttp_filter.filter(record)
    assert record.levelno == logging.INFO


def test_sanitize_filter() -> None:
    sanitize_filter = SanitizeFilter()

    # Test that it removes sensitive data in dict
    record = logging.LogRecord(
        name="some_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="",
        args={"auth": "secret", "email": "user@example.com", "notes": {"auth": "secret", "email": "user@example.com"}},
        exc_info=None,
    )
    assert sanitize_filter.filter(record)
    assert record.args == {"auth": "[REMOVED]", "email": "[REMOVED]", "notes": {"auth": "[REMOVED]", "email": "[REMOVED]"}}

    # Test that it doesn't remove non-sensitive data
    record = logging.LogRecord(
        name="some_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="",
        args={"name": "John Doe", "age": 30},
        exc_info=None,
    )
    assert sanitize_filter.filter(record)
    assert record.args == {"name": "John Doe", "age": 30}

    # Test that it removes sensitive data in tuple
    record = logging.LogRecord(
        name="some_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="",
        args=("email", "user@example.com"),
        exc_info=None,
    )
    assert sanitize_filter.filter(record)
    assert record.args == ("[REMOVED]", "[REMOVED]")
