"""Member plugin module."""

from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_routedef import AbstractRouteDef

from bumper.web.plugins import WebserverPlugin
from bumper.web.plugins.v1.private.member import handle_get_exp_by_scene

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
                handle_get_exp_by_scene,
            ),
        ]
