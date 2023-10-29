"""Lg plugin module."""
import json
import logging
import random
import string
from collections.abc import Iterable
from typing import Any
from xml.etree.ElementTree import Element

import defusedxml.ElementTree as ET
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import db, utils
from bumper.utils.settings import config as bumper_isc
from bumper.web import models

from .. import WebserverPlugin

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
    # EcoVacs Home
    random_id = "".join(random.sample(string.ascii_letters, 6))
    try:
        if bumper_isc.mqtt_helperbot is None:
            raise Exception("'bumper.mqtt_helperbot' is None")

        json_body: dict[str, Any] = json.loads(await request.text())
        did: str | None = json_body.get("did", None)

        if did is None:
            _LOGGER.error("No DID specified :: connected to MQTT")
        else:
            bot = db.bot_get(did)
            if bot is None or bot.get("company", "") != "eco-ng":
                _LOGGER.error(f"No bots with DID :: {did} :: connected to MQTT")
            else:
                if "cmdName" not in json_body and "td" in json_body:
                    json_body["cmdName"] = json_body.get("td")
                if "toId" not in json_body:
                    json_body["toId"] = did
                if "toType" not in json_body:
                    json_body["toType"] = bot.get("class")
                if "toRes" not in json_body:
                    json_body["toRes"] = bot.get("resource")
                if "payloadType" not in json_body:
                    json_body["payloadType"] = "x"
                if "payload" not in json_body:
                    # json_body["payload"] = ""
                    if json_body["td"] == "GetCleanLogs":
                        json_body["td"] = "q"
                        json_body["payload"] = '<ctl count="30"/>'

                body = await bumper_isc.mqtt_helperbot.send_command(json_body, random_id)
                _LOGGER.debug(f"Send Bot - {json_body}")
                _LOGGER.debug(f"Bot Response - {body}")
                try:
                    logs = []
                    if body.get("resp", None) is None:
                        _LOGGER.warning(f"lg logs return non 'resp': {json.dumps(body)}")
                    else:
                        logs_root: Element = ET.fromstring(body.get("resp"))
                        if logs_root.attrib.get("ret", "") == "ok":
                            for log_line in logs_root:
                                clean_log = {
                                    "ts": log_line.attrib.get("s"),
                                    "area": log_line.attrib.get("a"),
                                    "last": log_line.attrib.get("l"),
                                    "cleanType": log_line.attrib.get("t"),
                                    # imageUrl allows for providing images of cleanings, something to look into later
                                    # "imageUrl": "https://localhost:8007",
                                }
                                logs.append(clean_log)

                    body = {"ret": "ok", "logs": logs}
                    _LOGGER.debug(f"lg logs return: {json.dumps(body)}")
                    return web.json_response(body)
                except Exception as e:
                    _LOGGER.error(utils.default_exception_str_builder(e, json.dumps(body)), exc_info=True)
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, "during handling request"), exc_info=True)
    return web.json_response({"id": random_id, "errno": models.ERR_COMMON, "ret": "fail"})
