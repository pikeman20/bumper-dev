"""Ecms plugin module."""

from collections.abc import Iterable
from typing import Any

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.web.images import get_bot_image

from .. import WebserverPlugin


class EcmsPlugin(WebserverPlugin):
    """Ecms plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/ecms/file/get/{id}",
                # TODO: real response is a svga response
                get_bot_image,
            ),
            web.route(
                "*",
                "/ecms/app/ad/res",
                _handle_ad_res,
            ),
            web.route(
                "*",
                "/ecms/app/ad/res/v2",
                _handle_ad_res,
            ),
            web.route(
                "*",
                "/ecms/app/element/hint",
                _handle_hint,
            ),
            web.route(
                "*",
                "/ecms/app/resources",
                _handle_resources,
            ),
        ]


async def _handle_ad_res(_: Request) -> Response:
    """Ad res."""
    return web.json_response({"code": 0, "data": [], "message": "success", "success": True})


async def _handle_hint(request: Request) -> Response:
    """Hint."""
    codes = request.query.get("codes", "").split(",")
    data = {}
    for code in codes:
        data[code] = False
    return web.json_response({"code": 0, "data": data, "message": "success", "success": True})


async def _handle_resources(request: Request) -> Response:
    """Resources."""
    locations = request.query.get("locations", "")
    lang = request.query.get("lang", "en").lower()
    data: list[dict[str, Any]] = []

    if locations == "home_manage_intro":
        data = []
    elif locations == "robotui_func_ops":
        data = [
            {
                "action": {
                    "clickAction": "1",
                    "clickURL": f"https://adv-app.dc-na.ww.ecouser.net/pim/yiko_scene_newton.html?lang={lang}&defaultLang={lang}",
                },
                "content": "https://api-app.dc-as.ww.ecouser.net/api/ecms/file/get/62206001e50121388401de95",
                "description": "",
                "location": "robotui_func_ops",
                "resId": "622060a8e5012100b501e004",
                "tags": [
                    "n4gstt",
                    "3yqsch",
                    "p95mgv",
                    "jtmf04",
                    "lx3j7m",
                    "bro5wu",
                    "1vxt52",
                    "85nbtp",
                    "p1jij8",
                    "9ku8nu",
                    "2gab4o",
                ],
                "title": "",
                "type": "svga",
            }
        ]

    return web.json_response({"code": 0, "data": data, "message": "success", "success": True})
