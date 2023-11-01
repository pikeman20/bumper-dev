"""Member plugin module."""
import logging
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.web.response_utils import get_success_response

from ... import WebserverPlugin
from . import BASE_URL

_LOGGER = logging.getLogger(__name__)


class MemberPlugin(WebserverPlugin):
    """Member plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                f"{BASE_URL}member/getExpByScene",
                _handle_get_exp_by_scene,
            ),
        ]


async def _handle_get_exp_by_scene(request: Request) -> Response:
    """Get exp by scene."""
    # TODO: check what's needed to be implemented
    _LOGGER.warning("!!! POSSIBLE THIS API IS NOT (FULL) IMPLEMENTED :: _handle_get_exp_by_scene !!!")
    scene = request.query.get("scene")
    mid = request.query.get("mid", "")
    did = request.query.get("did", "")

    # GLOBALAPP_MACHINE_RENAME
    # GLOBALAPP_AREA_CATE_RENAME
    # GLOBALAPP_FIRST_SET_PERSONAL_CLEAN_MODULE
    # GLOBALAPP_SHOW_CLEAN_LOG
    # GLOBALAPP_USE_HELP_CENTER
    # GLOBALAPP_USE_SIDE_FILTER
    get_point = None
    prompt = None

    if mid == "" and did == "":
        if scene in ["GLOBALAPP_REGULATE_DEEBOT_SUCTION"]:
            get_point = 100
            prompt = "Task DEEBOT Perform suction power setting, +100"
        elif scene in ["GLOBALAPP_REGULATE_DEEBOT_WATER"]:
            get_point = 100
            prompt = "Perform task DEEBOT water flow rate, +100"
        elif scene in ["GLOBALAPP_TIMING_OF_CONSUMABLES"]:
            get_point = 50
            prompt = "Perform Display accessory usage task, +50"
        elif scene in ["GLOBALAPP_VIRTUAL_WALL_MANAGEMENT"]:
            get_point = 100
            prompt = "Perform task Manage DEEBOT Virtual Walls, +100"

    key_only_once1 = "only"  # only because
    key_only_once2 = "Once"  # of code spell :D
    return get_success_response(
        {
            "completeList": [
                {
                    "getExp": 0,
                    "getPoint": get_point,
                    f"{key_only_once1}{key_only_once2}": "N",
                    "prompt": prompt,
                }
            ]
        }
    )
