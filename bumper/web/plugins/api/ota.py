"""Ota plugin module."""

from collections.abc import Iterable
import logging

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import utils
from bumper.web.plugins import WebserverPlugin
from bumper.web.response_utils import response_success_v3

_LOGGER = logging.getLogger(__name__)


class OtaPlugin(WebserverPlugin):
    """Ota plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/ota/products/wukong/class/{class}/firmware/latest.json",
                _handle_products_firmware_latest,
            ),
        ]


async def _handle_products_firmware_latest(_: Request) -> Response:
    # TODO: check what's needed to be implemented
    utils.default_log_warn_not_impl("_handle_products_firmware_latest")
    # device_class = request.match_info.get("class")
    # did = request.query.get("did")
    return response_success_v3(data=None, result_key=None, include_success=True)
