"""User plugin module."""

from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.web import auth_util
from bumper.web.plugins import WebserverPlugin
from bumper.web.response_utils import get_success_response

from . import BASE_URL


class UserPlugin(WebserverPlugin):
    """User plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                f"{BASE_URL}user/checkLogin",
                auth_util.login,
            ),
            web.route(
                "*",
                f"{BASE_URL}user/checkAgreementBatch",
                _handle_check_agreement_batch,
            ),
        ]


async def _handle_check_agreement_batch(_: Request) -> Response:
    """Check agreement batch."""
    return get_success_response(
        {
            "agreementList": [],
            "reAcceptFlag": None,
            "userAcceptRecord": [
                {
                    "acceptTime": 1681542125538,
                    "force": None,
                    "id": "20230403095818_78798528690d2307bd692c0b624909f9",
                    "type": "USER",
                    "updateDesc": None,
                    "url": None,
                    "version": "1.03",
                },
                {
                    "acceptTime": 1681542128770,
                    "force": None,
                    "id": "20230322085808_ff1bcf0d24ece3a37e3dac81b7e91733",
                    "type": "PRIVACY",
                    "updateDesc": None,
                    "url": None,
                    "version": "1.07",
                },
            ],
        },
    )
