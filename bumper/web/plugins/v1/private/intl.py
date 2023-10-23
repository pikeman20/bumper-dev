"""Intl plugin module."""
import logging
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import db, utils

from ... import WebserverPlugin, get_success_response
from . import BASE_URL

_LOGGER = logging.getLogger("web_route_v1_priv_intl")


class IntlPlugin(WebserverPlugin):
    """Intl plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                f"{BASE_URL}intl/member/basicInfo",
                _handle_basic_info,
            ),
            web.route(
                "*",
                f"{BASE_URL}intl/member/signStatus",
                _handle_sign_status,
            ),
        ]


async def _handle_basic_info(request: Request) -> Response:
    try:
        user_devid = request.match_info.get("devid", "")
        user = db.user_by_device_id(user_devid)
        if user is None:
            _LOGGER.warning(f"No user found for {user_devid}")
        else:
            username = f"fusername_{user['userid']}"
            frozen_integral_desc = "The points will be credited to your member account 20 days after the payment of the order."

            return get_success_response(
                {
                    "availableGeneralIntegral": 9999,
                    "availableLimitedIntegral": 0,
                    "benefitList": [],
                    "expiringLimitedPointExplain": None,
                    "expiringLimitedPointShowDesc": None,
                    "expiringLimitedPoints": None,
                    "expiringPointDesc": None,
                    "expiringPointExplain": None,
                    "expiringPoints": None,
                    "frozenIntegral": 0,
                    "frozenIntegralDesc": frozen_integral_desc,
                    "goodsDetailIntegralDesc": "Redeem points for discounts!",
                    "integral": 9999,
                    "integralDescWapUrl": "https://gl-de-wap.ecovacs.com/web/page?no=jusapxaw",
                    "isCountryOpen": "Y",
                    "isLimitedIntegralOpen": "N",
                    "isMember": "Y",
                    "level": 1,
                    "levelIconUrl": "https://gl-us-pub.ecovacs.com/public/221027/f187b4b72f434fcc9eae655dbb389ac7.png",
                    "levelName": "VIP1",
                    "memberDescWapUrl": "https://club-eu-wap.ecovacs.com/DE/EN/content/description",
                    "remainingDay": None,
                    "shoppingGetIntegralShowDesc": None,
                    "shoppingGetIntegraltimes": None,
                    "shoppingGetIntegraltimesShowDesc": None,
                    "shoppingGetIntegraltimesUp": None,
                    "shoppingGetIntegraltimesUpShowDesc": None,
                    "signStatus": "SIGN",
                    "userHeadImg": None,
                    "userShowName": username,
                }
            )
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, "during handling request"), exc_info=True)
    raise HTTPInternalServerError


async def _handle_sign_status(_: Request) -> Response:
    return get_success_response({"signStatus": "SIGN"})
