"""Sds plugin module."""
import logging
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import utils

from .. import WebserverPlugin

_LOGGER = logging.getLogger(__name__)


class SdsPlugin(WebserverPlugin):
    """Sds plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/sds/baidu/audio/getcred",
                _handle,  # TODO: check how to handle correct
            ),
        ]


async def _handle(_: Request) -> Response:
    try:
        return web.json_response({"code": 0, "data": None, "message": "success"})
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, "during handling request"), exc_info=True)
    raise HTTPInternalServerError
