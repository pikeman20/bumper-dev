"""Agreement plugin module."""
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from ... import WebserverPlugin, get_success_response
from . import BASE_URL


class AgreementPlugin(WebserverPlugin):
    """Agreement plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                f"{BASE_URL}agreement/getUserAcceptInfo",
                _handle_get_user_accept_info,
            ),
        ]


async def _handle_get_user_accept_info(_: Request) -> Response:
    """Get user accept info."""
    url_1 = "https://gl-de-wap.ecovacs.com/content/agreement?id=20230403095818_78798528690d2307bd692c0b624909f9&language=EN"
    url_2 = "https://gl-de-wap.ecovacs.com/content/agreement?id=20230322085808_ff1bcf0d24ece3a37e3dac81b7e91733&language=EN"
    url_3 = "https://gl-de-wap.ecovacs.com/content/agreement?id=20230403095818_78798528690d2307bd692c0b624909f9&language=EN"
    url_4 = "https://gl-de-wap.ecovacs.com/content/agreement?id=20230322085808_ff1bcf0d24ece3a37e3dac81b7e91733&language=EN"
    return get_success_response(
        {
            "acceptList": [
                {
                    "acceptTime": 1681542125538,
                    "force": None,
                    "id": "20230403095818_78798528690d2307bd692c0b624909f9",
                    "type": "USER",
                    "updateDesc": None,
                    "url": url_1,
                    "version": "1.03",
                },
                {
                    "acceptTime": 1681542128770,
                    "force": None,
                    "id": "20230322085808_ff1bcf0d24ece3a37e3dac81b7e91733",
                    "type": "PRIVACY",
                    "updateDesc": None,
                    "url": url_2,
                    "version": "1.07",
                },
            ],
            "newestList": [
                {
                    "acceptTime": None,
                    "force": "N",
                    "id": "20230403095818_78798528690d2307bd692c0b624909f9",
                    "type": "USER",
                    "updateDesc": None,
                    "url": url_3,
                    "version": "1.03",
                },
                {
                    "acceptTime": None,
                    "force": "N",
                    "id": "20230322085808_ff1bcf0d24ece3a37e3dac81b7e91733",
                    "type": "PRIVACY",
                    "updateDesc": None,
                    "url": url_4,
                    "version": "1.07",
                },
            ],
        }
    )
