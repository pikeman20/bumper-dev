"""User plugin module."""
import logging
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import db, utils
from bumper.web import auth_util

from ... import WebserverPlugin, get_success_response
from . import BASE_URL

_LOGGER = logging.getLogger("web_route_v1_priv_user")


class UserPlugin(WebserverPlugin):
    """User plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                f"{BASE_URL}user/login",
                auth_util.login,
            ),
            web.route(
                "*",
                f"{BASE_URL}user/checkLogin",
                auth_util.login,
            ),
            web.route(
                "*",
                f"{BASE_URL}user/getAuthCode",
                auth_util.get_auth_code,
            ),
            web.route(
                "*",
                f"{BASE_URL}user/logout",
                _logout,
            ),
            web.route(
                "*",
                f"{BASE_URL}user/checkAgreement",
                _handle_check_agreement,
            ),
            web.route(
                "*",
                f"{BASE_URL}user/checkAgreementBatch",
                _handle_check_agreement_batch,
            ),
            web.route(
                "*",
                f"{BASE_URL}user/getUserAccountInfo",
                _handle_get_user_account_info,
            ),
            web.route(
                "*",
                f"{BASE_URL}user/getUserMenuInfo",
                _handle_get_user_menu_info,
            ),
            web.route(
                "*",
                f"{BASE_URL}/user/getMyUserMenuInfo",
                _handle_get_my_user_menu_info,
            ),
            web.route(
                "*",
                f"{BASE_URL}user/getMyUserMenuInfo",
                _handle_get_my_user_menu_info,
            ),
            web.route(
                "*",
                f"{BASE_URL}user/changeArea",
                _handle_change_area,
            ),
            web.route(
                "*",
                f"{BASE_URL}user/queryChangeArea",
                _handle_change_area,
            ),
            web.route(
                "*",
                f"{BASE_URL}user/acceptAgreementBatch",
                _handle_accept_agreement_batch,
            ),
        ]


async def _logout(request: Request) -> Response:
    try:
        user_device_id = request.match_info.get("devid", None)
        if user_device_id:
            user = db.user_by_device_id(user_device_id)
            if user:
                if db.check_token(user["userid"], request.query["accessToken"]):
                    # Deactivate old tokens and authcodes
                    db.user_revoke_token(user["userid"], request.query["accessToken"])

        return get_success_response(None)
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, None), exc_info=True)
    raise HTTPInternalServerError


async def _handle_get_user_account_info(request: Request) -> Response:
    try:
        user_devid = request.match_info.get("devid", "")
        user = db.user_by_device_id(user_devid)
        if user is None:
            _LOGGER.warning(f"No user found for {user_devid}")
        else:
            username = f"fusername_{user['userid']}"

            intl_member_info = {
                "availableGeneralIntegral": 0,
                "availableLimitedIntegral": 0,
                "benefitList": [],
                "expiringLimitedPointShowDesc": None,
                "expiringLimitedPoints": None,
                "expiringPointDesc": None,
                "expiringPointExplain": None,
                "expiringPoints": None,
                "frozenIntegral": 0,
                "frozenIntegralTips": "Points will be issued 20 days after order payment. Please wait.",
                "goodsDetailIntegralDesc": "Points will be issued 20 days after order payment. Please wait.",
                "integral": 0,
                "integralDescWapUrl": "https://gl-us-wap.ecovacs.com/web/page?no=hh3yxg4g",
                "intlMemberMallUrl": "https://www.ecovacs.com/us",
                "isCountryOpen": "Y",
                "isLimitedIntegralOpen": "N",
                "isMember": "Y",
                "levelName": "VIP1",
                "remainingDay": None,
                "vipLevelIconUrl": "https://gl-us-pub.ecovacs.com/public/220628/d01e939518354ee0af5c88a5269e27d8.png",
            }

            return get_success_response(
                {
                    "email": "null@null.com",
                    "hasMobile": "N",
                    "hasPassword": "Y",
                    "headIco": "",
                    "intlMemberInfo": intl_member_info,
                    "loginName": username,
                    "mobile": None,
                    "mobileAreaNo": None,
                    "nickname": "",
                    "obfuscatedMobile": None,
                    "thirdLoginInfoList": [{"accountType": "WeChat", "hasBind": "N"}],
                    "uid": f"fuid_{user['userid']}",
                    "userName": username,
                    "userShowName": username,
                }
            )
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, "during handling request"), exc_info=True)
    raise HTTPInternalServerError


async def _handle_check_agreement(request: Request) -> Response:
    app_type = request.match_info.get("apptype", "")
    data = []
    url_u = "https://gl-us-wap.ecovacs.com/content/agreement?id=20180804040641_7d746faf18b8cb22a50d145598fe4c90&language=EN"
    url_p = "https://gl-us-wap.ecovacs.com/content/agreement?id=20180804040245_4e7c56dfb7ebd3b81b1f2747d0859fac&language=EN"
    if "global_" in app_type:
        data = [
            {
                "force": "N",
                "id": "20180804040641_7d746faf18b8cb22a50d145598fe4c90",
                "type": "USER",
                "url": url_u,
                "version": "1.01",
            },
            {
                "force": "N",
                "id": "20180804040245_4e7c56dfb7ebd3b81b1f2747d0859fac",
                "type": "PRIVACY",
                "url": url_p,
                "version": "1.01",
            },
        ]
    return get_success_response(data)


async def _handle_check_agreement_batch(_: Request) -> Response:
    return get_success_response(
        {
            "agreementList": [],
            "reAcceptFlag": None,
            "userAcceptRecord": [
                {
                    "acceptTime": 1681542125538,
                    "force": None,
                    "id": "20230403095818_78798528690d2307bd692c0b624909f9",
                    "type": "USER",
                    "updateDesc": None,
                    "url": None,
                    "version": "1.03",
                },
                {
                    "acceptTime": 1681542128770,
                    "force": None,
                    "id": "20230322085808_ff1bcf0d24ece3a37e3dac81b7e91733",
                    "type": "PRIVACY",
                    "updateDesc": None,
                    "url": None,
                    "version": "1.07",
                },
            ],
        }
    )


async def _handle_get_user_menu_info(_: Request) -> Response:
    url_hf = "https://gl-us-pub.ecovacs.com/upload/global/2019/12/16/2019121603180741b73907046e742b80e8fe4a90fe2498.png"
    url_sr = "https://gl-us-pub.ecovacs.com/upload/global/2019/12/16/2019121603284185e632ec6c5da10bd82119d7047a1f9e.png"
    url_s = "https://gl-us-pub.ecovacs.com/upload/global/2019/12/16/201912160325324068da4e4a09b8c3973db162e84784d5.png"
    url_bs = "https://gl-us-pub.ecovacs.com/upload/global/2019/12/16/201912160325324068da4e4a09b8c3973db162e84784d5.png"
    return get_success_response(
        [
            {
                "menuItems": [
                    {
                        "clickAction": 1,
                        "clickUri": "https://ecovacs.zendesk.com/hc/en-us",
                        "menuIconUrl": url_hf,
                        "menuId": "20191216031849_4d744630f7ad2f5208a4b8051be61d10",
                        "menuName": "Help & Feedback",
                        "paramsJson": "",
                    }
                ],
                "menuPositionKey": "A_FIRST",
            },
            {
                "menuItems": [
                    {
                        "clickAction": 3,
                        "clickUri": "robotShare",
                        "menuIconUrl": url_sr,
                        "menuId": "20191216032853_5fac4cc9cbd0e166dfa951485d1d8cc4",
                        "menuName": "Share Robot",
                        "paramsJson": "",
                    }
                ],
                "menuPositionKey": "B_SECOND",
            },
            {
                "menuItems": [
                    {
                        "clickAction": 3,
                        "clickUri": "config",
                        "menuIconUrl": url_s,
                        "menuId": "20191216032545_ebea0fbb4cb02d9c2fec5bdf3371bc2d",
                        "menuName": "Settings",
                        "paramsJson": "",
                    }
                ],
                "menuPositionKey": "C_THIRD",
            },
            {
                "menuItems": [
                    {
                        "clickAction": 1,
                        "clickUri": "https://bumper.ecovacs.com/",
                        "menuIconUrl": url_bs,
                        "menuId": "20191216032545_ebea0fbb4cb02d9c2fec5bdf3371bc2c",
                        "menuName": "Bumper Status",
                        "paramsJson": "",
                    }
                ],
                "menuPositionKey": "D_FOURTH",
            },
        ]
    )


async def _handle_get_my_user_menu_info(_: Request) -> Response:
    icon_1 = "https://gl-us-pub.ecovacs.com/upload/global/2022/06/24/20220624060121_de0a8cbd8f8bb7941082679a23f70645.png"
    icon_2 = "https://gl-us-pub.ecovacs.com/upload/global/2022/12/14/20221214014704_9cc451e9c63a70a4bd6ada2089535267.png"
    icon_3 = "https://gl-us-pub.ecovacs.com/upload/global/2022/06/24/20220624060535_035aa1d9faf295f87f4193bcc94d7950.png"
    icon_4 = "https://gl-us-pub.ecovacs.com/upload/global/2022/06/24/20220624060711_db29f8c651a5682597eeed76e480b281.png"

    return get_success_response(
        {
            "menuList": [
                {
                    "menuItems": [
                        {
                            "clickAction": 3,
                            "clickUri": "glOrlderList",
                            "menuIconUrl": icon_1,
                            "menuId": "20220624060155_6729cbc2485200128c6ed986721d410e",
                            "menuName": "My Orders",
                            "menuSubName": "",
                            "paramsJson": "",
                            "redDotId": None,
                        },
                        {
                            "clickAction": 1,
                            "clickUri": "https://adv-app.dc-na.ww.ecouser.net/pim/third_party_voice_control.html",
                            "menuIconUrl": icon_2,
                            "menuId": "20221214014708_e105611ab873e21fca03995074a9b987",
                            "menuName": "Third-party Voice Control",
                            "menuSubName": None,
                            "paramsJson": "",
                            "redDotId": None,
                        },
                        {
                            "clickAction": 3,
                            "clickUri": "helpfbView",
                            "menuIconUrl": icon_3,
                            "menuId": "20220624060539_97ef192bb44d90e074353543a65f0f3a",
                            "menuName": "Help & Feedback",
                            "menuSubName": None,
                            "paramsJson": "",
                            "redDotId": None,
                        },
                        {
                            "clickAction": 3,
                            "clickUri": "config",
                            "menuIconUrl": icon_4,
                            "menuId": "20220624060714_b204f767cee480135ebdefd6e0a49195",
                            "menuName": "Settings",
                            "menuSubName": None,
                            "paramsJson": "",
                            "redDotId": None,
                        },
                    ],
                    "menuPositionKey": "MY_A",
                }
            ]
        }
    )


async def _handle_change_area(_: Request) -> Response:
    return get_success_response({"isNeedReLogin": "N"})


async def _handle_accept_agreement_batch(_: Request) -> Response:
    return get_success_response(None)
