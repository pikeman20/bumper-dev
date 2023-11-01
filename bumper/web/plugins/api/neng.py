"""Neng plugin module."""
import logging
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from .. import WebserverPlugin

_LOGGER = logging.getLogger(__name__)


class NengPlugin(WebserverPlugin):
    """Neng plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/neng/message/hasUnreadMsg",
                _handle_has_unread_message,
            ),
            web.route(
                "*",
                "/neng/message/getShareMsgs",
                _handle_get_share_msgs,
            ),
            web.route(
                "*",
                "/neng/message/getlist",
                _handle_get_list,
            ),
            web.route(
                "*",
                "/neng/message/read",
                _handle_read,
            ),
            web.route(
                "*",
                "/neng/v2/message/push",
                _handle_v2_message_push,
            ),
            web.route(
                "*",
                "/neng/v3/message/pushStatus",
                _handle_v3_message_push_status,
            ),
            web.route(
                "*",
                "/neng/v3/message/latest_by_did",
                _handle_v3_latest_by_did,
            ),
            web.route(
                "*",
                "/neng/v3/message/list",
                _handle_v3_message_list,
            ),
            web.route(
                "*",
                "/neng/v3/product/msg/tabs",
                _handle_v3_product_msg_tabs,
            ),
            web.route(
                "*",
                "/neng/v3/shareMsg/hasUnreadMsg",
                _handle_v3_share_msg_has_unread_msg,
            ),
        ]


async def _handle_has_unread_message(_: Request) -> Response:
    # EcoVacs Home
    return web.json_response({"code": 0, "data": {"hasUnRead": False, "shareMsgUnRead": False}})


async def _handle_get_share_msgs(_: Request) -> Response:
    # EcoVacs Home
    return web.json_response({"code": 0, "data": {"hasNext": False, "msgs": []}})


async def _handle_get_list(_: Request) -> Response:
    # EcoVacs Home
    return web.json_response({"code": 0, "data": {"hasNext": False, "msgs": []}})


async def _handle_read(_: Request) -> Response:
    # EcoVacs Home
    return web.json_response({"code": 0, "message": "success"})


async def _handle_v2_message_push(_: Request) -> Response:
    # EcoVacs Home
    # TODO: check what's needed to be implemented
    _LOGGER.warning("!!! POSSIBLE THIS API IS NOT (FULL) IMPLEMENTED :: _handle_v2_message_push !!!")
    return web.json_response({"code": 0, "data": "success", "message": ""})


async def _handle_v3_message_push_status(_: Request) -> Response:
    # EcoVacs Home
    # TODO: check what's needed to be implemented
    _LOGGER.warning("!!! POSSIBLE THIS API IS NOT (FULL) IMPLEMENTED :: _handle_v3_message_push_status !!!")
    # NOTE: devices has a list with dict of did,msgPushStatus,nickName
    # NOTE: uid is as userid in header. not implemented
    return web.json_response(
        {
            "code": 0,
            "data": {
                "devices": [],
                "msgPushStatus": {"DEVICE": True, "SHARE": True},
                "uid": "",
            },
            "message": "success",
        }
    )


async def _handle_v3_latest_by_did(_: Request) -> Response:
    # EcoVacs Home
    return web.json_response({"code": 0, "data": [], "message": "success"})


async def _handle_v3_message_list(_: Request) -> Response:
    # EcoVacs Home
    return web.json_response({"code": 0, "data": [], "message": "success"})


async def _handle_v3_product_msg_tabs(_: Request) -> Response:
    # EcoVacs Home
    return web.json_response(
        {
            "code": 0,
            "data": [
                {
                    "code": "evt",
                    "name": "Work messages",
                },
                {
                    "code": "error",
                    "name": "Malfunction messages",
                },
            ],
            "message": "success",
        }
    )


async def _handle_v3_share_msg_has_unread_msg(_: Request) -> Response:
    # EcoVacs Home
    return web.json_response(
        {
            "code": 0,
            "data": {"count": 0, "unRead": False},
            "message": "success",
        }
    )
