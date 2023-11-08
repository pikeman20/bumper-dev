"""Dln plugin module."""
import logging
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import db, utils
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
    try:
        did: str | None = request.query.get("did")
        log_type: str = request.query.get("logType", "")
        data = []

        if did is None:
            _LOGGER.error("No DID specified :: connected to MQTT")
        elif log_type == "clean":
            bot = db.bot_get(did)
            if bot is None or bot.get("company", "") != "eco-ng":
                _LOGGER.error(f"No bots with DID :: {did} :: connected to MQTT")
            else:
                clean_logs = db.clean_log_by_id(did)
                for clean_log in clean_logs:
                    log = clean_log.as_dict()
                    log.update({"did": did})
                    data.append(log)

        return response_success_v3(sorted(data, key=lambda x: x["ts"], reverse=True))
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
