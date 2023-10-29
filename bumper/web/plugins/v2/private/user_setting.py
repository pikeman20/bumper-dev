"""User setting plugin module."""

from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from ... import WebserverPlugin, get_success_response
from . import BASE_URL


class UserSettingPlugin(WebserverPlugin):
    """User setting plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                f"{BASE_URL}userSetting/getMsgReceiveSetting",
                _handle_get_msg_receive_setting,
            ),
        ]


async def _handle_get_msg_receive_setting(_: Request) -> Response:
    """Get msg receive setting."""
    return get_success_response(
        {
            "list": [
                {
                    "name": "Promotion messages",
                    "openOrClose": "Y",
                    "settingType": "ACTIVITY",
                },
                {
                    "name": "Service notifications",
                    "openOrClose": "Y",
                    "settingType": "SERVICE_NOTIFICATION",
                },
                {
                    "name": "Customer service messages",
                    "openOrClose": "Y",
                    "settingType": "CUSTOMER_SERVICE",
                },
            ]
        }
    )
