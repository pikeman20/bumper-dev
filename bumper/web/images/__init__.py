"""Web image module."""

import logging
from pathlib import Path

from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request

from bumper.utils import utils

_LOGGER = logging.getLogger(__name__)


async def get_bot_image(_: Request) -> FileResponse:
    """Return image of bot."""
    try:
        return FileResponse(Path(__file__).parent / "robotvac_image.jpg")
    except Exception:
        _LOGGER.exception(utils.default_exception_str_builder())
    raise HTTPInternalServerError
