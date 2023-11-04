"""Pim consumable plugin module."""
import logging
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import utils
from bumper.web.plugins import WebserverPlugin
from bumper.web.response_utils import response_success_v7

_LOGGER = logging.getLogger(__name__)


class ConsumablePlugin(WebserverPlugin):
    """Consumable plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/consumable/getPurchaseUrl",
                _handle_get_purchase_url,
            ),
        ]


async def _handle_get_purchase_url(_: Request) -> Response:
    """Get purchas url."""
    # TODO: check what's needed to be implemented
    utils.default_log_warn_not_impl("_handle_get_exp_by_scene")
    try:
        return response_success_v7([])
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, "during handling request"), exc_info=True)
    raise HTTPInternalServerError
