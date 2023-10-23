"""Homed plugin module."""
import json
import logging
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import utils

from .. import WebserverPlugin

_LOGGER = logging.getLogger("web_route_api_homed")


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
        body = {
            "code": 0,
            "data": [
                {
                    "createTime": utils.get_current_time_as_millis(),
                    "createUser": request.query.get("userid"),
                    "createUserName": request.query.get("userid"),
                    "firstCreate": False,
                    "homeId": "781a0733923f2240cf304757",
                    "name": "My Home",
                    "type": "own",
                }
            ],
            "message": "success",
        }
        return web.json_response(body)
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, "during handling request"), exc_info=True)
    raise HTTPInternalServerError


async def _handle_home_create(request: Request) -> Response:
    """Home create."""
    # TODO: check what's needed to be implemented
    post_body = json.loads(await request.text())
    name = post_body.get("name")
    _LOGGER.debug(f"Create {name}")

    return web.json_response({"code": 0, "message": "success"})


async def _handle_home_delete(request: Request) -> Response:
    """Home delete."""
    # TODO: check what's needed to be implemented
    post_body = json.loads(await request.text())
    homeId = post_body.get("homeId")  # pylint: disable=invalid-name
    _LOGGER.debug(f"Delete {homeId}")

    return web.json_response({"code": 0, "message": "success"})


async def _handle_member_list(request: Request) -> Response:
    """Member list."""
    # TODO: check what's needed to be implemented
    home_id = request.query.get("homeId")

    return web.json_response(
        {
            "code": 0,
            "data": [
                {
                    "createTime": utils.get_current_time_as_millis(),
                    "id": home_id,
                    "isAdmin": 2,
                    "name": "null@null.null",
                    "roleId": "",
                    "roleName": "",
                    "status": 1,
                    "uid": "",
                }
            ],
            "message": "success",
        }
    )


async def _handle_device_move(request: Request) -> Response:
    """Device move."""
    # TODO: check what's needed to be implemented
    post_body = json.loads(await request.text())
    did = post_body.get("did")
    mid = post_body.get("mid")
    res = post_body.get("res")
    to = post_body.get("to")
    _LOGGER.debug(f"Move {did} {mid} {res} {to}")

    return web.json_response({"code": 0, "message": "success"})
