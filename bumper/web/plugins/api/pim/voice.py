"""Voice plugin module."""
# import logging
from collections.abc import Iterable

from aiohttp import web

# from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

# from bumper.utils import utils
from bumper.web.plugins import WebserverPlugin

# _LOGGER = logging.getLogger("web_route_pim_voice")


class VoicePlugin(WebserverPlugin):
    """Voice plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/voice/get",
                _handle_get,
            ),
        ]


async def _handle_get(_: Request) -> Response:
    """Get."""
    # TODO: check how to implement
    return web.json_response(
        {
            "code": 0,
            "data": [],
        }
    )
