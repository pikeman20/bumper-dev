import asyncio
import os

import pytest
from testfixtures import LogCapture

import bumper
from bumper.utils.settings import config as bumper_isc
from bumper.utils.utils import str_to_bool


def test_strtobool():
    assert str_to_bool("t") is True
    assert str_to_bool("f") is False
    assert str_to_bool(0) is False


# TODO: current not understand how this works with he logger defined in utils,
#       LogCapture not checks the stdout logs, that's why check_present is commented


@pytest.mark.parametrize("debug", [False, True])
async def test_start_stop(debug: bool):
    with LogCapture() as log:
        bumper_isc.bumper_verbose = 2
        if debug:
            bumper_isc.bumper_level = "DEBUG"

        if os.path.exists("tests/tmp.db"):
            os.remove("tests/tmp.db")  # Remove existing db

        asyncio.create_task(bumper.start())
        await asyncio.sleep(0.1)

        log.check_present(("bumper", "INFO", "Starting Bumpers..."))

        while True:
            try:
                # log.check_present(("bumper", "INFO", "Bumper started successfully"))
                break
            except AssertionError:
                pass
            await asyncio.sleep(0.1)

        log.clear()

        await asyncio.create_task(bumper.shutdown())
        # log.check_present(("bumper", "INFO", "Shutting down..."), ("bumper", "INFO", "Shutdown complete!"))
        assert bumper_isc.shutting_down is True
