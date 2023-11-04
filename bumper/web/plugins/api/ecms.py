"""Ecms plugin module."""

import logging
from collections.abc import Iterable
from typing import Any

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import utils
from bumper.web.images import get_bot_image
from bumper.web.response_utils import response_success_v6

from .. import WebserverPlugin

_LOGGER = logging.getLogger(__name__)


class EcmsPlugin(WebserverPlugin):
    """Ecms plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/ecms/file/get/{id}",
                # TODO: real response is a svga response
                get_bot_image,
            ),
            web.route(
                "*",
                "/ecms/app/ad/res",
                _handle_ad_res,
            ),
            web.route(
                "*",
                "/ecms/app/ad/res/v2",
                _handle_ad_res,
            ),
            web.route(
                "*",
                "/ecms/app/element/hint",
                _handle_hint,
            ),
            web.route(
                "*",
                "/ecms/app/resources",
                _handle_resources,
            ),
            web.route(
                "*",
                "/ecms/app/push/event",
                _handle_push_event,
            ),
        ]


async def _handle_ad_res(_: Request) -> Response:
    """Ad res."""
    # REQUEST EXAMPLES
    # => V1
    # {
    #     "appVer": "2.4.1",
    #     "channel": "google_play",
    #     "country": "DE",
    #     "lang": "EN",
    #     "notReceive": ["INTRODUCTION", "MARKETING", "QUESTIONNAIRE"],
    #     "platform": "android",
    #     "record": [],
    #     "scode": "robotui_config",
    #     "tags": [],
    #     "timeZone": "GMT+8",
    #     "uid": "REPLACED_UID",
    #     "ver": "2.4.1",
    #
    #     # opt 1:
    #     "location": ["robot_device_list_first"],
    #     # opt 2:
    #     "location": ["robot_home_winbot", "robot_home_deebot", "robot_home_airbot"]
    # }
    #
    # => v2
    # {
    #     "notReceive": ["MARKETING", "QUESTIONNAIRE", "INTRODUCTION"],
    #     "uid": "ckiqxr4cfb062946",
    #
    #     opt 1:
    #     "tags": [],
    #     "location": ["ad_launch"],
    #     "timeZone": "GMT+2",
    #
    #     opt 2:
    #     "tags": [],
    #     "location": ["ad_main_pop"],
    #     "timeZone": "GMT+2",
    #
    #     opt 3:
    #     "tags": ["yna5xi"],
    #     "location": ["ad_controler_pop"],
    #     "timeZone": "GMT+2",
    #
    #     opt 3 (two different opt for loc):
    #     "location": [
    #       "robot_control_index_func_ops",
    #       "robot_contorl_main_promotion",
    #       "robot_contorl_main_promotion_pop",
    #       "robot_contorl_silver_ion",
    #       "robot_control_aes_buy",
    #       "ad_card_control_pop"
    #     ],
    #     "location": ["ad_main_bottom_control_popover"],
    #     "tags": ["mid:p95mgv", "sn:E09C15674D1FP7DF0304"],
    #     "auth": {},
    #     "channel": "google_play",
    #     "timeZone": 60
    # }

    return response_success_v6([])


async def _handle_hint(request: Request) -> Response:
    """Hint."""
    # TODO: check what's needed to be implemented
    utils.default_log_warn_not_impl("_handle_hint")
    codes = request.query.get("codes", "").split(",")
    data = {}
    for code in codes:
        data[code] = True  # DEBUG: default saw only False
    return response_success_v6(data)


async def _handle_resources(request: Request) -> Response:
    """Resources."""
    locations = request.query.get("locations", "")
    lang = request.query.get("lang", "en").lower()
    data: list[dict[str, Any]] = []

    if locations == "home_manage_intro":
        data = []
    elif locations == "robotui_func_ops":
        data = [
            {
                "action": {
                    "clickAction": "1",
                    "clickURL": f"https://adv-app.dc-na.ww.ecouser.net/pim/yiko_scene_newton.html?lang={lang}&defaultLang={lang}",
                },
                "content": "https://api-app.dc-as.ww.ecouser.net/api/ecms/file/get/62206001e50121388401de95",
                "description": "",
                "location": "robotui_func_ops",
                "resId": "622060a8e5012100b501e004",
                "tags": [
                    "n4gstt",
                    "3yqsch",
                    "p95mgv",
                    "jtmf04",
                    "lx3j7m",
                    "bro5wu",
                    "1vxt52",
                    "85nbtp",
                    "p1jij8",
                    "9ku8nu",
                    "2gab4o",
                ],
                "title": "",
                "type": "svga",
            }
        ]
    if len(data) <= 0:
        _LOGGER.error(f"locations is not know :: {locations}")
    return response_success_v6(data)


async def _handle_push_event(_: Request) -> Response:
    """Ad res."""
    # dataCategory = request.query.get("dataCategory", "Discover-Hint")
    # resourceId = request.query.get("resourceId", "Robot")
    return response_success_v6("ok")
