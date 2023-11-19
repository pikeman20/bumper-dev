"""Pim dictionary plugin module."""
from collections.abc import Iterable
import logging

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import utils
from bumper.web.plugins import WebserverPlugin

_LOGGER = logging.getLogger(__name__)


class DictionaryPlugin(WebserverPlugin):
    """Dictionary plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/dictionary/getErrDetail",
                _handle_get_err_detail,
            ),
        ]


async def _handle_get_err_detail(_: Request) -> Response:
    """Get error details."""
    try:
        return web.json_response(
            {
                "code": -1,
                "data": [],
                "msg": "This errcode's detail is not exists",
            }
        )
    except Exception as e:
        _LOGGER.exception(utils.default_exception_str_builder(e, "during handling request"))
    raise HTTPInternalServerError
