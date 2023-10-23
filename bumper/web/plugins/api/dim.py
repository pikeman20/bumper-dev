"""Dim plugin module."""
import json
import logging
import random
import string
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import db
from bumper.utils.settings import config as bumper_isc
from bumper.utils.utils import default_exception_str_builder
from bumper.web import models

from .. import WebserverPlugin

_LOGGER = logging.getLogger("web_route_api_dim")


class DimPlugin(WebserverPlugin):
    """Dim plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "POST",
                "/dim/devmanager.do",
                _handle_dev_manager,
            ),
        ]


async def _handle_dev_manager(request: Request) -> Response:
    """Dev Manager."""
    # EcoVacs Home
    try:
        if bumper_isc.mqtt_helperbot is None:
            raise Exception("'bumper.mqtt_helperbot' is None")

        json_body = json.loads(await request.text())

        random_id = "".join(random.sample(string.ascii_letters, 6))
        did = json_body.get("toId", None)

        if did is not None:
            bot = db.bot_get(did)
            if bot is not None and bot.get("company", "") == "eco-ng" and bot["mqtt_connection"]:
                body = await bumper_isc.mqtt_helperbot.send_command(json_body, random_id)
                _LOGGER.debug(f"Send Bot - {json_body}")
                _LOGGER.debug(f"Bot Response - {body}")
                return web.json_response(body)

            # No response, send error back
            _LOGGER.error(f"No bots with DID :: {json_body.get('toId')} :: connected to MQTT")
            return web.json_response({"id": random_id, "errno": models.ERR_COMMON, "ret": "fail"})

        td = json_body.get("td", None)
        if td is not None:
            if td == "PollSCResult":  # Seen when doing initial wifi config
                return web.json_response({"ret": "ok"})

            if td == "HasUnreadMsg":  # EcoVacs Home
                return web.json_response({"ret": "ok", "unRead": False})

            if td == "ReceiveShareDevice":  # EcoVacs Home
                return web.json_response({"ret": "ok"})
    except Exception as e:
        _LOGGER.error(default_exception_str_builder(e, "during handling request"), exc_info=True)
    raise HTTPInternalServerError
