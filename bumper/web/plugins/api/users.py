"""Users plugin module."""

from collections.abc import Iterable, Mapping
import json
import logging
from typing import Any

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import db, utils
from bumper.utils.settings import config as bumper_isc
from bumper.web import auth_util
from bumper.web.plugins import WebserverPlugin
from bumper.web.response_utils import response_error_v6, response_success_v9

_LOGGER = logging.getLogger(__name__)


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
    try:
        body = None
        post_body: Mapping[str, Any]
        if request.content_type == "application/x-www-form-urlencoded":
            post_body = await request.post()
        else:
            post_body = json.loads(await request.text())

        todo = post_body.get("todo", "")

        # NOTE: seams not anymore available
        if todo == "FindBest":
            service = post_body.get("service", "")
            if service == "EcoMsgNew":
                srv_ip = bumper_isc.bumper_announce_ip
                srv_port = bumper_isc.XMPP_LISTEN_PORT_TLS
                _LOGGER.info(f"Announcing EcoMsgNew Server to bot as: {srv_ip}:{srv_port}")
                body = web.json_response({"ip": srv_ip, "port": srv_port, "result": "ok"})
            elif service == "EcoUpdate":
                srv_ip = bumper_isc.ECOVACS_UPDATE_SERVER
                srv_port = bumper_isc.ECOVACS_UPDATE_SERVER_PORT
                _LOGGER.info(f"Announcing EcoMsgNew Server to bot as: {srv_ip}:{srv_port}")
                body = web.json_response({"ip": srv_ip, "port": srv_port, "result": "ok"})

        if todo == "loginByItToken":
            if "userId" in post_body:
                if db.check_auth_code(post_body["userId"], post_body["token"]):
                    body = web.json_response(
                        {
                            "resource": post_body["resource"],
                            "result": "ok",
                            "todo": "result",
                            "token": post_body["token"],
                            "userId": post_body["userId"],
                        },
                    )
            else:  # EcoVacs Home LoginByITToken
                login_token = db.login_by_it_token(post_body["token"])
                if login_token:
                    body = web.json_response(
                        {
                            "resource": post_body["resource"],
                            "result": "ok",
                            "todo": "result",
                            "token": login_token["token"],
                            "userId": login_token["userid"],
                        },
                    )

        if todo == "GetAuthCode":
            # TODO: check what's needed to be implemented, which token is really needed and how to get correct
            utils.default_log_warn_not_impl("_handle_user/GetAuthCode")
            body = await auth_util.get_auth_code_v2(request)

        if todo == "GetDeviceList":
            body = web.json_response({"devices": db.bot_get_all(), "result": "ok", "todo": "result"})

        if todo == "SetDeviceNick":
            db.bot_set_nick(post_body.get("did"), post_body.get("nick"))
            body = response_success_v9()

        if todo == "AddOneDevice":
            db.bot_set_nick(post_body.get("did"), post_body.get("nick"))
            body = response_success_v9()

        if todo == "DeleteOneDevice":
            db.bot_remove(post_body["did"])
            body = response_success_v9()

        if body is None:
            _LOGGER.error(f"todo is not know :: {todo}")
            body = response_error_v6(todo)
        return body
    except Exception:
        _LOGGER.exception(utils.default_exception_str_builder(info="during handling request"))
    raise HTTPInternalServerError
