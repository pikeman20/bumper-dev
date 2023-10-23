"""Member plugin module."""
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from ... import WebserverPlugin, get_success_response
from . import BASE_URL


class MemberPlugin(WebserverPlugin):
    """Member plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                f"{BASE_URL}member/getExpByScene",
                _handle_get_exp_by_scene,
            ),
        ]


async def _handle_get_exp_by_scene(request: Request) -> Response:
    """Get exp by scene."""
    # TODO: check what needs to be implemented
    scene = request.query.get("scene")
    if scene == "GLOBALAPP_MACHINE_RENAME":
        pass
    return get_success_response(None)
