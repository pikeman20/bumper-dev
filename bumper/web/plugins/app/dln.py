"""Dln plugin module."""
import logging
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import utils
from bumper.web.response_utils import response_success_v3

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
            web.route(
                "*",
                "/dln/api/log/clean_result/del",
                _handle_clean_result_del,
            ),
        ]


async def _handle_clean_result_list(request: Request) -> Response:
    """Clean result list."""
    # TODO: check what's needed to be implemented
    utils.default_log_warn_not_impl("_handle_clean_result_list")
    try:
        did = request.query.get("did")
        log_type = request.query.get("logType")
        data = []

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
            # EXAMPLE
            data.append(
                {
                    "aiavoid": 0,
                    "aiopen": 0,
                    "aitypes": [],
                    "aq": 0,
                    "area": 1,
                    "cleanId": "987456321",
                    "cornerDeep": 0,
                    "did": did,
                    "enablePowerMop": 0,
                    "id": "123456789",
                    "imageUrl": "https://portal-ww.ecouser.net/app/dln/api/log/clean_result/image?id=123456789",
                    "last": 60,
                    "mapName": "",
                    "powerMopType": 1,
                    "sceneName": "",
                    "stopReason": 3,
                    "triggerMode": 0,
                    "ts": utils.get_current_time_as_millis(),
                    "type": "auto",
                }
            )

        return response_success_v3(data)
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, "during handling request"), exc_info=True)
    raise HTTPInternalServerError


async def _handle_clean_result_del(_: Request) -> Response:
    """Clean result delete."""
    # TODO: check what's needed to be implemented
    utils.default_log_warn_not_impl("_handle_clean_result_del")
    try:
        return response_success_v3(None)
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, "during handling request"), exc_info=True)
    raise HTTPInternalServerError
