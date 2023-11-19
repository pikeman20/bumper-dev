"""Lg plugin module."""
from collections.abc import Iterable
import json
import logging
from typing import Any

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import db, utils
from bumper.web.plugins import WebserverPlugin
from bumper.web.response_utils import response_error_v7

_LOGGER = logging.getLogger(__name__)


class LgPlugin(WebserverPlugin):
    """Lg plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "POST",
                "/lg/log.do",
                _handle_lg_log,
            ),
        ]


async def _handle_lg_log(request: Request) -> Response:
    """Clean result list."""
    try:
        json_body: dict[str, Any] = json.loads(await request.text())
        did: str | None = json_body.get("did")
        td: str = json_body.get("td", "")
        logs = []

        if did is None:
            _LOGGER.error("No DID specified :: connected to MQTT")
        elif td == "GetCleanLogs":
            bot = db.bot_get(did)
            if bot is None or bot.get("company", "") != "eco-ng":
                _LOGGER.error(f"No bots with DID :: {did} :: connected to MQTT")
            else:
                clean_logs = db.clean_log_by_id(did)
                for clean_log in clean_logs:
                    logs.append(clean_log.as_dict())

        return web.json_response(
            {
                "ret": "ok",
                "logs": sorted(logs, key=lambda x: x["ts"], reverse=True),
            }
        )
    except Exception as e:
        _LOGGER.exception(utils.default_exception_str_builder(e, "during handling request"))
    return response_error_v7()
