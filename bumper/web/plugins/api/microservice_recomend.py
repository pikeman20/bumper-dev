"""Microservice recommend plugin module."""
import logging
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import utils
from bumper.web.response_utils import response_success_v6

from .. import WebserverPlugin

_LOGGER = logging.getLogger(__name__)


class MicroserviceRecomendPlugin(WebserverPlugin):
    """Microservice recommend plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/microservice-recomend/userReminderResult/",
                _handle_user_reminder_result,
            ),
        ]


async def _handle_user_reminder_result(_: Request) -> Response:
    # TODO: check what's needed to be implemented
    utils.default_log_warn_not_impl("_handle_user_reminder_result")
    try:
        return response_success_v6(None)
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, "during handling request"), exc_info=True)
    raise HTTPInternalServerError
