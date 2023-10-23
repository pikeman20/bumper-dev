"""Rapp plugin module."""
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from .. import WebserverPlugin


class RappPlugin(WebserverPlugin):
    """Rapp plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/rapp/sds/user/data/map/get",
                _handle_map_get,
            ),
            web.route(
                "*",
                "/rapp/sds/user/data/del",
                _handle_user_data_del,
            ),
        ]


async def _handle_map_get(_: Request) -> Response:
    """Map get."""
    return web.json_response(
        {
            "code": 0,
            "data": {
                "data": {"name": "My Home"},
                "tag": None,
            },
            "message": "success",
        }
    )


async def _handle_user_data_del(_: Request) -> Response:
    """Map get."""
    return web.json_response({"code": 0, "data": None, "message": "success"})
