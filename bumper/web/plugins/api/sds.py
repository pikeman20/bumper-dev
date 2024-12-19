"""Sds plugin module."""

from collections.abc import Iterable
import logging

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import utils
from bumper.web.plugins import WebserverPlugin
from bumper.web.response_utils import response_success_v6

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
        return response_success_v6(None)
    except Exception:
        _LOGGER.exception(utils.default_exception_str_builder(info="during handling request"))
    raise HTTPInternalServerError
