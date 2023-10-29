"""Dln plugin module."""
import logging
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import utils

from .. import WebserverPlugin

_LOGGER = logging.getLogger(__name__)


class DlnPlugin(WebserverPlugin):
    """Dln plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/dln/api/log/clean_result/list",
                _handle_clean_result_list,
            ),
        ]


async def _handle_clean_result_list(request: Request) -> Response:
    """Clean result list."""
    # TODO: check what's needed to be implemented
    try:
        did = request.query.get("did")
        log_type = request.query.get("logType")

        # did:         REPLACED
        # res:         Gy2C
        # country:     DE
        # size:        10
        # auth:        REPLACED
        # version:     v2
        # logType:     clean
        # before:      1698540667000
        # lang:        EN
        # et1:         1698540667778
        # defaultLang: zh_cn
        # channel:     google_play

        if log_type == "clean":
            _LOGGER.debug(f"Log type for :: did: {did}")

        return web.json_response({"code": 0, "data": [], "message": "success"})
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, "during handling request"), exc_info=True)
    raise HTTPInternalServerError
