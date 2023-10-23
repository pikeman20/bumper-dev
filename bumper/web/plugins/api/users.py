"""Users plugin module."""
import json
import logging
from collections.abc import Iterable, Mapping
from typing import Any

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import db, utils
from bumper.utils.settings import config as bumper_isc

from .. import WebserverPlugin

_LOGGER = logging.getLogger("web_route_api_users")


class UsersPlugin(WebserverPlugin):
    """Users plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "POST",
                "/users/user.do",
                _handle_user,
            ),
        ]


async def _handle_user(request: Request) -> Response:
    """User do."""
    # if request.method == "GET":  # Skip GET for now
    #     return web.json_response({"result": "fail", "todo": "result"})

    try:
        body: dict[str, Any] | str = {"result": "fail", "todo": "result"}
        post_body: Mapping[str, Any]
        if request.content_type == "application/x-www-form-urlencoded":
            post_body = await request.post()
        else:
            post_body = json.loads(await request.text())

        todo = post_body.get("todo", "")

        if todo == "FindBest":
            service = post_body.get("service", "")
            if service == "EcoMsgNew":
                srv_ip = bumper_isc.bumper_announce_ip
                srv_port = bumper_isc.XMPP_LISTEN_PORT_TLS
                _LOGGER.info(f"Announcing EcoMsgNew Server to bot as: {srv_ip}:{srv_port}")
                body = json.dumps({"ip": srv_ip, "port": srv_port, "result": "ok"})
                # NOTE: bot seems to be very picky about having no spaces, only way was with text
                body = body.replace(" ", "")

            elif service == "EcoUpdate":
                srv_ip = bumper_isc.ECOVACS_UPDATE_SERVER
                srv_port = bumper_isc.ECOVACS_UPDATE_SERVER_PORT
                _LOGGER.info(f"Announcing EcoMsgNew Server to bot as: {srv_ip}:{srv_port}")
                body = {"ip": srv_ip, "port": srv_port, "result": "ok"}

        elif todo == "loginByItToken":
            if "userId" in post_body:
                if db.check_authcode(post_body["userId"], post_body["token"]):
                    body = {
                        "resource": post_body["resource"],
                        "result": "ok",
                        "todo": "result",
                        "token": post_body["token"],
                        "userId": post_body["userId"],
                    }
            else:  # EcoVacs Home LoginByITToken
                login_token = db.login_by_it_token(post_body["token"])
                if login_token:
                    body = {
                        "resource": post_body["resource"],
                        "result": "ok",
                        "todo": "result",
                        "token": login_token["token"],
                        "userId": login_token["userid"],
                    }

        elif todo == "GetAuthCode":
            # TODO: check how provide token
            user_id = post_body.get("auth", {}).get("userid")
            token = post_body.get("auth", {}).get("token")
            if user_id is not None and token is not None:
                token = db.user_get_token(user_id, token)
                if token and "authcode" in token:
                    auth_code = token["authcode"]
                    body = {
                        "code": auth_code,
                        "result": "ok",
                        "todo": "result",
                    }

        elif todo == "GetDeviceList":
            body = {"devices": db.bot_get_all(), "result": "ok", "todo": "result"}

        elif todo == "SetDeviceNick":
            db.bot_set_nick(post_body["did"], post_body["nick"])
            body = {"result": "ok", "todo": "result"}

        elif todo == "AddOneDevice":
            db.bot_set_nick(post_body["did"], post_body["nick"])
            body = {"result": "ok", "todo": "result"}

        elif todo == "DeleteOneDevice":
            db.bot_remove(post_body["did"])
            body = {"result": "ok", "todo": "result"}

        return web.json_response(body)
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, "during handling request"), exc_info=True)
    raise HTTPInternalServerError
