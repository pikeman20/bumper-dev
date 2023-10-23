"""Common plugin module."""
import json
import logging
import os
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from bumper.utils import db, utils
from bumper.utils.settings import config as bumper_isc

from ... import WebserverPlugin, get_success_response
from . import BASE_URL

_LOGGER = logging.getLogger("web_route_v1_priv")


class CommonPlugin(WebserverPlugin):
    """Common plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                f"{BASE_URL}common/checkAPPVersion",
                _handle_check_app_version,
            ),
            web.route(
                "*",
                f"{BASE_URL}common/checkVersion",
                _handle_check_version,
            ),
            web.route(
                "*",
                f"{BASE_URL}common/uploadDeviceInfo",
                _handle_upload_device_info,
            ),
            web.route(
                "*",
                f"{BASE_URL}common/getSystemReminder",
                _handle_get_system_reminder,
            ),
            web.route(
                "*",
                f"{BASE_URL}common/getConfig",
                _handle_get_config,
            ),
            web.route(
                "*",
                f"{BASE_URL}common/getUserConfig",
                _handle_get_user_config,
            ),
            web.route(
                "*",
                f"{BASE_URL}common/getAreas",
                _handle_get_areas,
            ),
            web.route(
                "*",
                f"{BASE_URL}common/getAgreementURLBatch",
                _handle_get_agreement_url_batch,
            ),
            web.route(
                "*",
                f"{BASE_URL}common/getTimestamp",
                _handle_get_timestamp,
            ),
            web.route(
                "*",
                f"{BASE_URL}common/getBottomNavigateInfoList",
                _handle_get_bottom_navigate_info_list,
            ),
            web.route(
                "*",
                f"{BASE_URL}common/getAboutBriefItem",
                _handle_get_about_brief_item,
            ),
        ]


async def _handle_check_version(_: Request) -> Response:
    return get_success_response(
        {
            "c": None,
            "img": None,
            "r": 0,
            "t": None,
            "u": None,
            "ut": 0,
            "v": None,
        }
    )


async def _handle_check_app_version(_: Request) -> Response:
    return get_success_response(
        {
            "c": None,
            "downPageUrl": None,
            "img": None,
            "nextAlertTime": None,
            "r": 0,
            "t": None,
            "u": None,
            "ut": 0,
            "v": None,
        }
    )


async def _handle_upload_device_info(_: Request) -> Response:
    return get_success_response({"devicePushRegisterResult": "N"})


async def _handle_get_system_reminder(_: Request) -> Response:
    return get_success_response(
        {
            "iosGradeTime": {"iodGradeFlag": "N"},
            "openNotification": {
                "openNotificationContent": None,
                "openNotificationFlag": "N",
                "openNotificationTitle": None,
            },
        }
    )


async def _handle_get_config(request: Request) -> Response:
    try:
        data: list[dict[str, str]] = []
        for key in request.query["keys"].split(","):
            if key == "PUBLIC.KEY.CONFIG":
                with open(bumper_isc.server_cert, "rb") as cert_file:
                    cert_data = cert_file.read()
                cert = x509.load_pem_x509_certificate(cert_data, default_backend())
                public_key_bytes = cert.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
                public_key = "".join(public_key_bytes.decode("utf-8").strip().split("\n")[1:-1])
                data.append({"key": key, "value": f'{{"publicKey":"{public_key}"}}'})

            elif key == "EMAIL.REGISTER.CONFIG":
                data.append({"key": key, "value": '{"needVerify":"N"}'})

            elif key == "OPEN.APP.CERTIFICATE.CONFIG":
                data.append({"key": key, "value": '{"ISO27001":"ENABLED","TUV":"ENABLED"}'})

            elif key == "USER.DATA.COLLECTION":
                data.append({"key": key, "value": "Y"})

            else:
                data.append({"key": key, "value": "Y"})

        return get_success_response(data)
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, "during handling request"), exc_info=True)
    raise HTTPInternalServerError


async def _handle_get_user_config(request: Request) -> Response:
    try:
        user_devid = request.match_info.get("devid", "")
        user = db.user_by_device_id(user_devid)
        if user:
            username = f"fusername_{user['userid']}"
            return get_success_response(
                {
                    "saTraceConfig": {
                        "collectionStatus": "ENABLED",
                        "isTrace": "Y",
                        "saUserId": username,
                        "serverUrl": "https://sa-eu-datasink.ecovacs.com/sa?project=production",
                    }
                }
            )
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, "during handling request"), exc_info=True)
    raise HTTPInternalServerError


async def _handle_get_areas(_: Request) -> Response:
    try:
        with open(os.path.join(os.path.dirname(__file__), "common_area.json"), encoding="utf-8") as file:
            return get_success_response(json.load(file))
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, "during handling request"), exc_info=True)
    raise HTTPInternalServerError


async def _handle_get_agreement_url_batch(_: Request) -> Response:
    url_u: str = "https://gl-eu-wap.ecovacs.com/content/agreement?id=20180804040641_7d746faf18b8cb22a50d145598fe4c90&language=EN"
    url_p: str = "https://gl-eu-wap.ecovacs.com/content/agreement?id=20180804040245_4e7c56dfb7ebd3b81b1f2747d0859fac&language=EN"
    return get_success_response(
        [
            {
                "acceptTime": None,
                "force": None,
                "id": "20180804040641_7d746faf18b8cb22a50d145598fe4c90",
                "type": "USER",
                "url": url_u,
                "version": "1.03",
            },
            {
                "acceptTime": None,
                "force": None,
                "id": "20180804040245_4e7c56dfb7ebd3b81b1f2747d0859fac",
                "type": "PRIVACY",
                "url": url_p,
                "version": "1.03",
            },
        ]
    )


async def _handle_get_timestamp(_: Request) -> Response:
    return get_success_response({"timestamp": utils.get_current_time_as_millis()})


async def _handle_get_about_brief_item(_: Request) -> Response:
    return get_success_response([])


async def _handle_get_bottom_navigate_info_list(_: Request) -> Response:
    url_robot_1 = "https://gl-us-pub.ecovacs.com/upload/global/2023/05/09/20230509015020_b1503be93bea4cc11d75bf350f3c188d.png"
    url_robot_2 = "https://gl-us-pub.ecovacs.com/upload/global/2023/05/09/20230509015024_8e854006dd2b049460c96dea89604909.png"
    url_store_1 = "https://gl-us-pub.ecovacs.com/upload/global/2023/05/09/20230509015030_13ea2faef0d0908af8a3a6486a678eef.png"
    url_store_2 = "https://gl-us-pub.ecovacs.com/upload/global/2023/05/09/20230509015033_9af971ffdf084a11b153fd3753418d92.png"
    url_store_3 = "https://www.ecovacs.com/us?utm_source=ecovacsGlobalApp&utm_medium=Appshopclick_US&utm_campaign=Menu_US"
    url_mine_1 = "https://gl-us-pub.ecovacs.com/upload/global/2023/05/09/20230509015037_d8126eaa65d38935cbb6283cca2a0519.png"
    url_mine_2 = "https://gl-us-pub.ecovacs.com/upload/global/2023/05/09/20230509015041_0e8b6fb3428ae8aac6a0c04a81e26525.png"
    return get_success_response(
        [
            {
                "bgImgUrl": None,
                "defaultImgUrl": url_robot_1,
                "iconId": "20230509015048_e6d8aafd16e80fe0d3ec893be8f40b32",
                "iconName": "Robot",
                "iconType": "ROBOT",
                "lightImgUrl": url_robot_2,
                "lightNameRgb": "#005EB8",
                "mediaType": None,
                "mediaUrl": "NULL",
                "positionType": "Robot",
                "tabItemActionUrl": None,
            },
            {
                "bgImgUrl": None,
                "defaultImgUrl": url_store_1,
                "iconId": "20230509015048_fa825040a65166c17bafdadc718df095",
                "iconName": "Store",
                "iconType": "MALL",
                "lightImgUrl": url_store_2,
                "lightNameRgb": "#005EB8",
                "mediaType": None,
                "mediaUrl": "NULL",
                "positionType": "Store",
                "tabItemActionUrl": url_store_3,
            },
            {
                "bgImgUrl": None,
                "defaultImgUrl": url_mine_1,
                "iconId": "20230509015048_04732bdb41f45b3510e9fd0adc6dc008",
                "iconName": "Mine",
                "iconType": "MINE",
                "lightImgUrl": url_mine_2,
                "lightNameRgb": "#005EB8",
                "mediaType": None,
                "mediaUrl": "NULL",
                "positionType": "Mine",
                "tabItemActionUrl": None,
            },
        ]
    )
