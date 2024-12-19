"""Homed plugin module."""

from collections.abc import Iterable
import json
import logging
from typing import Any
import uuid

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import db, utils
from bumper.utils.settings import config as bumper_isc
from bumper.web.plugins import WebserverPlugin
from bumper.web.response_utils import response_success_v3, response_success_v8

_LOGGER = logging.getLogger(__name__)


class HomedPlugin(WebserverPlugin):
    """Homed plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/homed/home/list",
                _handle_home_list,
            ),
            web.route(
                "POST",
                "/homed/home/create",
                _handle_home_create,
            ),
            web.route(
                "*",
                "/homed/home/update",
                _handle_home_update,
            ),
            web.route(
                "POST",
                "/homed/home/delete",
                _handle_home_delete,
            ),
            web.route(
                "*",
                "/homed/member/list",
                _handle_member_list,
            ),
            web.route(
                "POST",
                "/homed/device/move",
                _handle_device_move,
            ),
        ]


async def _handle_home_list(request: Request) -> Response:
    """Home list."""
    try:
        user_id = request.query.get("userid")
        data = []
        if user_id is not None:
            user = db.user_by_user_id(user_id)
            if user is not None:
                for index, home_id in enumerate(user.homeids):
                    data.append(
                        {
                            "createTime": utils.get_current_time_as_millis(),
                            "createUser": user.userid,
                            "createUserName": user.username,
                            "firstCreate": False,
                            "homeId": home_id,
                            "name": f"My Home ({index})",
                            "type": "own",
                        },
                    )
        return response_success_v3(data)
    except Exception:
        _LOGGER.exception(utils.default_exception_str_builder(info="during handling request"))
    raise HTTPInternalServerError


async def _handle_home_create(request: Request) -> Response:
    """Home create."""
    # TODO: check what's needed to be implemented
    utils.default_log_warn_not_impl("_handle_home_create")
    json_body: dict[str, Any] = json.loads(await request.text())
    token = request.headers.get("authorization")
    name = json_body.get("name")
    if token is not None:
        user_id = db.user_id_by_token(token.split(" ")[1])
        if user_id is not None:
            db.user_add_home(user_id, uuid.uuid4().hex)
            _LOGGER.debug(f"Create :: {name}")
    return response_success_v8()


async def _handle_home_update(request: Request) -> Response:
    """Home update."""
    # TODO: check what's needed to be implemented
    utils.default_log_warn_not_impl("_handle_home_update")
    json_body = json.loads(await request.text())
    home_id = json_body.get("homeId")
    name = json_body.get("name")
    _LOGGER.debug(f"Update :: homeId: {home_id} - name: {name}")
    return response_success_v8()


async def _handle_home_delete(request: Request) -> Response:
    """Home delete."""
    # TODO: check what's needed to be implemented
    utils.default_log_warn_not_impl("_handle_home_delete")
    json_body = json.loads(await request.text())
    home_id = json_body.get("homeId")
    user = db.user_by_home_id(home_id)
    if user is not None:
        db.user_remove_home(user.userid, home_id)
    _LOGGER.debug(f"Delete :: {home_id}")
    return response_success_v8()


async def _handle_member_list(request: Request) -> Response:
    """Member list."""
    # TODO: check what's needed to be implemented
    utils.default_log_warn_not_impl("_handle_member_list")
    try:
        home_id = request.query.get("homeId", bumper_isc.HOME_ID)
        user = db.user_by_home_id(home_id)
        if user is None:
            _LOGGER.warning(f"No user found for {home_id}")
        else:
            return response_success_v3(
                [
                    {
                        "createTime": utils.get_current_time_as_millis(),
                        "id": user.userid,
                        "isAdmin": 2,
                        "name": "null@null.com",
                        "roleId": "",
                        "roleName": "",
                        "status": 1,
                        "uid": user.userid,
                    },
                ],
            )

    except Exception:
        _LOGGER.exception(utils.default_exception_str_builder(info="during handling request"))
    raise HTTPInternalServerError


async def _handle_device_move(request: Request) -> Response:
    """Device move."""
    # TODO: check what's needed to be implemented
    utils.default_log_warn_not_impl("_handle_device_move")
    post_body = json.loads(await request.text())
    did = post_body.get("did")
    mid = post_body.get("mid")
    res = post_body.get("res")
    to = post_body.get("to")
    _LOGGER.debug(f"Move :: did: {did} - mid: {mid} - res: {res} - to: {to}")

    return response_success_v8()
