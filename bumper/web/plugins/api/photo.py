"""Photo plugin module."""
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


class PhotoPlugin(WebserverPlugin):
    """Photo plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/photo/list",
                _handle,
            ),
        ]


async def _handle(_: Request) -> Response:
    # TODO: check what's needed to be implemented, which token is really needed and how to get correct
    utils.default_log_warn_not_impl("photo/list")
    try:
        return response_success_v6(None)
    except Exception as e:
        _LOGGER.exception(utils.default_exception_str_builder(e, "during handling request"))
    raise HTTPInternalServerError
