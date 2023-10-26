import asyncio
import os

import pytest
from testfixtures import LogCapture

import bumper
from bumper.utils.settings import config as bumper_isc
from bumper.utils.utils import strtobool


def test_strtobool():
    assert strtobool("t") is True
    assert strtobool("f") is False
    assert strtobool(0) is False


@pytest.mark.parametrize("debug", [False, True])
async def test_start_stop(debug: bool):
    with LogCapture() as log:
        if os.path.exists("tests/tmp.db"):
            os.remove("tests/tmp.db")  # Remove existing db

        bumper_isc.bumper_verbose = 2
        if debug:
            bumper_isc.bumper_level = "DEBUG"

        asyncio.create_task(bumper.start())
        await asyncio.sleep(0.1)

        log.check_present(("INFO", "bumper", "Starting Bumpers..."))
        while True:
            try:
                log.check_present(("INFO", "bumper", "Bumper started successfully"))
                break
            except AssertionError:
                pass
            await asyncio.sleep(0.1)

        log.clear()

        await bumper.shutdown()
        log.check_present(("INFO", "bumper", "Shutting down..."), ("INFO", "bumper", "Shutdown complete!"))
        assert bumper_isc.shutting_down is True
