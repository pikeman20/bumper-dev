"""Appsvr plugin module."""

from collections.abc import Iterable, Mapping
import copy
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
from bumper.web.response_utils import response_error_v5, response_success_v3, response_success_v4, response_success_v5

from .pim import get_product_iot_map

_LOGGER = logging.getLogger(__name__)


class AppsvrPlugin(WebserverPlugin):
    """Appsvr plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "POST",
                "/appsvr/app.do",
                _handle_app_do,
            ),
            web.route(
                "*",
                "/appsvr/app/config",
                _handle_app_config,
            ),
            web.route(
                "*",
                "/appsvr/improve",
                _handle_improve,
            ),
            web.route(
                "*",
                "/appsvr/improve/accept",
                _handle_improve_accept,
            ),
            web.route(
                "*",
                "/appsvr/improve/user/accept",
                _handle_improve_user_accept,
            ),
            web.route(
                "*",
                "/appsvr/notice/home",
                _handle_notice_home,
            ),
            web.route(
                "*",
                "/appsvr/notice/list",
                _handle_notice_list,
            ),
            web.route(
                "*",
                "/appsvr/oauth_callback",
                _handle_oauth_callback,
            ),
            web.route(
                "*",
                "/appsvr/service/list",
                _handle_service_list,
            ),
            web.route(
                "*",
                "/appsvr/ota/firmware",
                _handle_ota_firmware,
            ),
            web.route(
                "*",
                "/appsvr/device/blacklist/check",
                _handle_device_blacklist_check,
            ),
            web.route(
                "*",
                "/appsvr/akvs/start_watch",
                _handle_akvs_start_watch,
            ),
        ]


async def _handle_app_do(request: Request) -> Response:
    """App do."""
    try:
        post_body: Mapping[str, Any]
        if request.content_type == "application/x-www-form-urlencoded":
            post_body = await request.post()
        else:
            post_body = json.loads(await request.text())

        todo = post_body.get("todo", "")

        if todo == "GetGlobalDeviceList":
            return response_success_v4(create_device_list(), data_key="devices")

        if todo == "GetCodepush":
            return response_success_v4(
                {
                    "extend": {},
                    "type": "microsoft",
                    "url": "",
                },
            )

        if todo == "RobotControl":
            # TODO: check what's needed to be implemented
            utils.default_log_warn_not_impl("_handle_app_do/RobotControl")
            did = post_body.get("did", "")
            data_ctl: dict[str, Any] | None = post_body.get("data", {}).get("ctl", None)
            if data_ctl is None:
                return response_error_v5()
            cmd = next(iter(data_ctl.keys()))
            # cmd_request = MQTTCommandModel(data_ctl.get(cmd), version="p2p")
            # await bumper_isc.mqtt_helperbot.send_command(cmd_request)  # TODO: check if correct used and finish implementation
            # NOTE: Faked response for now
            ret_type = None
            if cmd == "GetBatteryInfo":
                ret_type = {"key": "power", "value": "100"}
            elif cmd == "GetChargeState":
                ret_type = {"key": "type", "value": "Idle"}
            if cmd in {"Charge", "Clean"}:
                return response_success_v4({cmd: {"ret": "ok", "did": did}})
            if ret_type is not None:
                return response_success_v4({cmd: {"ret": "ok", "did": did, ret_type["key"]: ret_type["value"]}})

        if todo == "GetAppVideoUrl":
            keys = post_body.get("keys", [])
            data = {}
            for key in keys:
                if key == "t9_promotional_video":
                    data[key] = f"https://{bumper_isc.DOMAIN_ALI}/public/t9_promotional_video.mp4"
            return response_success_v4(data)

        if todo == "GetDeviceProtocolV2":
            return response_success_v4(
                {
                    "video": {
                        "version": "13.01",
                        "hasNewProtocol": False,
                        "hasReadOld": True,
                        "isAccept": True,
                        "protocolUrl": (
                            f"https://{bumper_isc.DOM_SUB_PORT}/api/pim/protocol.html?version=13.01"
                            "&lang=en&defaultLang=en&country=DE&type=video"
                        ),
                    },
                    "improve": {
                        "version": "11.15",
                        "hasNewProtocol": False,
                        "hasReadOld": True,
                        "isAccept": False,
                        "protocolUrl": (
                            f"https://{bumper_isc.DOM_SUB_PORT}/api/pim/protocol.html?version=11.15"
                            "&lang=en&defaultLang=en&country=DE&type=improve"
                        ),
                    },
                },
            )

        _LOGGER.warning(f"todo is not know :: {todo}")
        return response_error_v5()
    except Exception:
        _LOGGER.exception(utils.default_exception_str_builder(info="during handling request"))
    raise HTTPInternalServerError


async def _handle_app_config(request: Request) -> Response:
    """App config."""
    code = request.query.get("code", "")
    data: list[dict[str, Any]] | None = None
    configurl = f"codepush-base.{bumper_isc.DOM_SUB_1}{bumper_isc.DOMAIN_MAIN}"
    backupurl = f"codepush-base.{bumper_isc.DOM_SUB_1}{bumper_isc.DOMAIN_MAIN}"
    contenturl = f"adv-app.{bumper_isc.DOM_SUB_1}{bumper_isc.DOMAIN_MAIN}"

    if code == "app_lang_enum":
        data = [
            {
                "resId": "622ee4977404d4518fd575fb",
                "code": "app_lang_enum",
                "name": "APP 语言枚举列表",
                "description": "",
                "type": "json",
                "content": {
                    "ar": "العربية",
                    "cs": "český",
                    "da": "Dansk",
                    "nl": "Nederlands",
                    "zh": "普通话",
                    "zh_cn": "普通话",
                    "zh-hans": "简体中文",
                    "zh-hant": "繁體中文",
                    "en": "English",
                    "en-us": "English(American)",
                    "en-au": "English(Australian)",
                    "en-ca": "English(Canadian)",
                    "en-in": "English(Indian)",
                    "en-gb": "English(United Kingdom)",
                    "et": "Eesti",
                    "he": "עברי",
                    "hu": "Magyar",
                    "id": "Indonesia",
                    "lv": "Latvijas",
                    "lt": "Lietuvos",
                    "no": "Norsk språk",
                    "fa": "فارسی",
                    "pl": "Polski",
                    "pt": "Português",
                    "sv": "Svenska",
                    "hk": "粤語",
                    "tw": "國語",
                    "th": "ไทย",
                    "tr": "Türkçe",
                    "my": "Malay",
                    "de": "Deutsch",
                    "fr": "Français",
                    "es": "Español",
                    "it": "Italiano",
                    "ru": "Pусский",
                    "sk": "Slovenský jazyk",
                    "ko": "한국어",
                    "vn": "Tiếng Việt",
                    "ja": "日本語",
                },
            },
        ]

    elif code == "codepush_config":
        data = [
            {
                "resId": "614d73873d80d1deed8be299",
                "code": "codepush_config",
                "name": "global codepush",
                "description": "",
                "type": "json",
                "content": {
                    "ssh5": {
                        "deploymentKey": {
                            "production": "AwV60bVIL5-f_bsQubbR5Cr3p-7lKg0wIKhdF4K",
                            "staging": "14aVIqRTytjYFnAeZckI4j6-Sc310GVP1797TS",
                            "current": "production",
                        },
                        "configurl": configurl,
                        "version": "1.0.0",
                    },
                    "keplervideomaph5": {
                        "deploymentKey": {
                            "production": "ndCZmhLHNUtpS_QkL1QRR9N6ccvZ8G9nCvTuVyx",
                            "staging": "XPmjd5N4bvfDVm3JrC6ORM7uplmbuxCTbT9oV-",
                            "current": "production",
                        },
                        "configurl": configurl,
                        "version": "1.0.0",
                    },
                    "y2h5": {
                        "deploymentKey": {
                            "production": "4VjXXho7kXaRs5SPBQeMOHgzqHZm2lQKYMSChX",
                            "staging": "apKOSI2XaYAAtWgdMIlNhLhw2kO0kVA7UjKKW",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "x2bohrh5": {
                        "deploymentKey": {
                            "production": "KAEyod25NeWXYYx976kjCSLClF6-YJ0NPg_CSa",
                            "staging": "DK17gATrQx1_EN6S2ouwPVKw265nXSJJeiTvr",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "x2clbh5": {
                        "deploymentKey": {
                            "production": "SmkoYd7iUIo8INaYKFYitRDVytmueykOVIApAW",
                            "staging": "DalPnnqGngr20aSJhgLice2O0P15MEfv2F5ug",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "netDiagno": {
                        "deploymentKey": {
                            "production": "1YhT34XSJJ-iUPtrBsi-zXA1LPCyAtLjsEW7IU",
                            "staging": "Cqn5Kl-UYcru2RYKN9xJvMHaA7lWAmd7d-vli",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "robotDiscovery": {
                        "deploymentKey": {
                            "production": "z94xCOc2FnBqdw6IJMFvMoWFLALxVNGsK0wHuJ",
                            "staging": "w3nVjj2mBV1JdO8tBO2JcU8EL4W6nBrv8KOVo",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "language": {
                        "deploymentKey": {
                            "production": "mQ7b_ImAD5t_hapi17Dt_CK0ZU1nArKrTYdCTI",
                            "staging": "IPbEkwK4wD9MCzWtncXQ8C0lDdLQxOMn13Owg",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "winbot": {
                        "deploymentKey": {
                            "production": "QEdpHlrNp1ANHhYFbEJ63dYo1bcsZCShQ9H938",
                            "staging": "uYmbjPDsvnfIBjjY9pM0PdESrZX8_QxMpm-bH",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "beluga": {
                        "deploymentKey": {
                            "production": "vhaH5f2nNpKiXPFDhVq6yf4gr6xFGAOKoMGTFT",
                            "staging": "RT1aLYD7YwQms9vs539Qn5GjRlExVWeMTOHeF",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "hwPush": {
                        "deploymentKey": {
                            "production": "4cPMrbntK2vbs-KRgsrJq4HI0W-hrTHP1BMTKq",
                            "staging": "dXgPCPco60Fc_JlZ5S_bS0ZanhlaNiU9elFaj",
                            "current": "production",
                        },
                        "version": "1.0.0",
                    },
                    "t10More": {
                        "deploymentKey": {
                            "production": "RSYAx668chaf0tpKvf1kJNaVJmDzi4g83wsg78",
                            "staging": "yQeevYX5q1yVhr_dH0VwKNJ3x3iDBSxJ-E91G",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "test20": {
                        "deploymentKey": {
                            "production": "n1MBCZHFWVi3PFdxg-u6N7yF6CStEXtlKms3O",
                            "staging": "vCmfAvE-g-OkOvLm8ckIfjLwf1c9a-fBGI6u2",
                            "current": "production",
                        },
                        "version": "1.0.0",
                    },
                    "at90": {
                        "deploymentKey": {
                            "production": "1W2Lw4KvqTz0D-UMxzfZSEcv2yWpoD7SZyGzb4",
                            "staging": "bokwAmqkL-svCnwI8Fd1pGSHBSf-aBoXWtNyi",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "bruceMore": {
                        "deploymentKey": {
                            "production": "P5sN80W6TdO5nQ63CJWvtTgnu-BKYqxQmf8IEi",
                            "staging": "1FXFufgsGXUcHc2F7eLWPPDXDsVySG9sj5VKc",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "furniture": {
                        "deploymentKey": {
                            "production": "VKfJlwYCG58sJN3FfCjYGqRd2M81HCIn2kOBrw",
                            "staging": "M7lyba6OXxVBG_KrkIgbv569Jnwz6V1gdk0oA",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "bruce3dRes": {
                        "deploymentKey": {
                            "production": "uOtNaTLAbWAFiQhovEqW4nyhvUbSxFNF92vdiV",
                            "staging": "4mm6F3Jak4JtMwO2AMHlbTHElUOMWZd_IzL5P",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "2.1.4",
                    },
                    "t10H5": {
                        "deploymentKey": {
                            "production": "mackERM5dTh8cqiAk9MEBuRhdgLEytf1emmE4H",
                            "staging": "f93aQ5QrspoyG5vYvPTICrfmS65YJVNFuNJ0o",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "x1proH5": {
                        "deploymentKey": {
                            "production": "Wt3wZa8Hs69dbZgtNXsiNVcda9P-GBSBDm4lDw",
                            "staging": "UvSn3tgPRYfmhwT7YOwP4WO5Us6HKC-sq91HS",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "andyproH5": {
                        "deploymentKey": {
                            "production": "SmTGB14wfXJnTZ0iHh03tEq83S9j6vK_B0zI9s",
                            "staging": "zhiPemGhbl0FV3V8_kBY9luOBgLd55YwYuImG",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "avacq": {
                        "deploymentKey": {
                            "production": "GxNUohEV_hHSw6Gap-StWiW9gTnP32-QIgkoVb",
                            "staging": "5FfFTL-ZIKF2ixpcX_E5Sua8Ixqn55Mpg6W_q",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "andyprocq": {
                        "deploymentKey": {
                            "production": "4BNGgbVnlX72LzmReCJ6Wk8kip7-r7Ryzvq3ML",
                            "staging": "Q-nsZ6qHNNen-Dse_2r6XlxW0bHhDu-ZaV-0H",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "feedback": {
                        "deploymentKey": {
                            "production": "WItFnpEfp-Rbc2B9hfLeuinBr03GZ-JhH2T4HO",
                            "staging": "C_PwRTI0NRVP9F3OBxYXRC8UvLrneiXnsvztE",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "bruce3DH5": {
                        "deploymentKey": {
                            "production": "hNnGhKA8jkPLQfmT9VVLWJMvssRIADF3s65tfD",
                            "staging": "iAz1OvOFinTA6DcotZL4hVFK9P1-9gEc63Syb",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "t93DH5": {
                        "deploymentKey": {
                            "production": "SfL1sY_6V3jXpve1cm0P1NbWqdDBoGlhCAfs0j",
                            "staging": "IVlc9Cp2zblCoF06DpPONjEud0I1I1WgKVF9L",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "t9aivi3DH5": {
                        "deploymentKey": {
                            "production": "xfpg077WmAycqI0avmPp2CEneEbPudBW-cIdOO",
                            "staging": "WSXU46W-20J2FJYW9cp46zglU7ou9-vGOQpP1",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "x2omnih5": {
                        "deploymentKey": {
                            "production": "aDSKvlow04p5n8c-E3VyqMFu4uUqtGHPl9QPdW",
                            "staging": "xScQMVfxtwE-2zxua1W5ErV5VcDIRV2dNftu3",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "t103DH5": {
                        "deploymentKey": {
                            "production": "0XLlHQNfNd0YUpiD-gDe1h6oIctlsVKwpcmViH",
                            "staging": "9ShOioxbphO8yAj2eCH9dxdokNkey5fUESL1O",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "n10H5": {
                        "deploymentKey": {
                            "production": "XvkGE1ck0ryXYrKiZfLkey8rLaGQrdJrK6NbhT",
                            "staging": "P7Tc7dKMMw_2rsNYnjL8avKNGBvZwFGgWXc3S",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "at91": {
                        "deploymentKey": {
                            "production": "DWfSnnORMkobKsaS3V0e7VMGVwSiHZqEvtEsJA",
                            "staging": "XVbaPU2hBbzAWC4FvpLR_Jr14pTYdZqQQYzj-",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "goat": {
                        "deploymentKey": {
                            "production": "M2oNdmHoQQT57oQ8BmfUQJtEirFCtm9eJVxZm2",
                            "staging": "Yb_c8B9JHVqY_WLajIurkKaUTG4TGVkLyXYj-",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "z2h5": {
                        "deploymentKey": {
                            "production": "PYBJrRsobI0I0daHnkZ-NQ5Y0p8CdmXEBeFlgJ",
                            "staging": "JOh7dYs9kfQmfKDt7efqjnvvqWGsoyQeshDOS",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "common_h5_wificonfig": {
                        "deploymentKey": {
                            "production": "5qjDOMa4u1euqWEwqEZD6jimbrAemeiaRV_CZ7",
                            "staging": "QHW58TtxPsWGjmZ50kNxAA0HTyS_Z-SB0Arr1",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "at92": {
                        "deploymentKey": {
                            "production": "gkhxiPWw5-v7UPEj0ImuPLMBME57DqrNmMHdtt",
                            "staging": "XutZcQwGKVM2bXjxa-xej1bTkKn7DbZuNGav-",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "goatWifiConfig": {
                        "deploymentKey": {
                            "production": "vsSrYLDXjkI7QPGkF3YghqQRoioIkQLtg2jn6Q",
                            "staging": "nhcEIBlRsXGOHySHFtHnNirZl4Nm4ZvgJGk9C",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "w2": {
                        "deploymentKey": {
                            "production": "bjPgGQImxLfkkwaGfJSdiOQJjqY8zePT0Zn3EE",
                            "staging": "IVU5ksl1Pg6LCxY6E_0Z7y4gZlSiR8N-skdXT",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "bluetooth_detect": {
                        "deploymentKey": {
                            "production": "ZZ4sMVW8D4aLSFq5-2sBop1cEdAGDgTzcC5WDU",
                            "staging": "L1wUtnf9yb52PDqldFJiHkV9AXphuh4814NA-",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "t30h5": {
                        "deploymentKey": {
                            "production": "FKk06D18kgJF89hmXCNYM9QOr3_XhCQ57H2S_G",
                            "staging": "KyAMEVANA1hGBFwc53QPpHN3dy7Atxp51jW93",
                            "current": "production",
                        },
                        "backupurl": backupurl,
                        "version": "1.0.0",
                    },
                    "y30h5": {
                        "version": "1.0.0",
                        "backupurl": backupurl,
                        "deploymentKey": {
                            "current": "production",
                            "production": "26p8nXPBq_eugaHR-cVBFil_ef7YYiVE68PjbT",
                            "staging": "MM16kaUHzbh_ptTsN1Fb35A_B86JHtlRNQwgD",
                        },
                    },
                    "bohrsubh5": {
                        "version": "1.0.0",
                        "backupurl": backupurl,
                        "deploymentKey": {
                            "current": "production",
                            "production": "NBFPr3pQMpwD5HMSvlo2kqc3NhsGjGJn-eC9Vd",
                            "staging": "76lZI9XfdwOprE2zj0xsfd5LrJ6LsZHwLLcz0",
                        },
                    },
                    "bohrh5": {
                        "version": "1.0.0",
                        "backupurl": backupurl,
                        "deploymentKey": {
                            "current": "production",
                            "production": "bxoAxfmnUrBiA10VESVZO4CkTmVySR0JwRACg8",
                            "staging": "9SjZJJvyFOmfMCTZc1PIwa-TjjGnaDnyYhZgi",
                        },
                    },
                    "goatx": {
                        "version": "1.0.0",
                        "backupurl": backupurl,
                        "deploymentKey": {
                            "current": "production",
                            "production": "FYrj_wRehjTJv19ELubhoVdz7YlcZj-KQ66Q8G",
                            "staging": "YO2F7sbZRNIH8gC8tZrQHRiwG1jksFMzwn69I",
                        },
                    },
                    "fsh5": {
                        "version": "1.0.0",
                        "backupurl": backupurl,
                        "deploymentKey": {
                            "current": "production",
                            "production": "S0nmh8PmK7Z6kr-hZEO1rv_sRQEcic5G7nfhxR",
                            "staging": "QHK_k60AYl5sXaOqeu6CiUTpaFIxtx0Dce2cW",
                        },
                    },
                    "keplerh5": {
                        "version": "1.0.0",
                        "backupurl": backupurl,
                        "deploymentKey": {
                            "current": "production",
                            "production": "xTtjPf2Q0Ydo-NHvqHHukvnq2oqN1Ybb1Tr8QC",
                            "staging": "tXdizL3qf6Q8RzoxXG_OY3wX-EpF6CDq7Bi-V",
                        },
                    },
                    "t30mixproh5": {
                        "version": "1.0.0",
                        "backupurl": backupurl,
                        "deploymentKey": {
                            "current": "production",
                            "production": "d5pv56U3n9eSixagTb7IFdzOU18OGfyUYyde7H",
                            "staging": "OY0hPAqO8eUeDK0_7-mKsXrP7WpFZGz2dYHyF",
                        },
                    },
                    "faradayh5": {
                        "version": "1.0.0",
                        "backupurl": backupurl,
                        "deploymentKey": {
                            "current": "production",
                            "production": "r3hqBPMQgR3jEjKCoGfEZ_EQ-dwJpJ3o08Q764",
                            "staging": "kC6b-hLyFvxlcHKvzMyumOLvK6EEBewWoDFzh",
                        },
                    },
                    "wshark": {
                        "version": "1.0.0",
                        "backupurl": backupurl,
                        "deploymentKey": {
                            "current": "production",
                            "production": "GNvUH5F6DzZUNqQKH6NLohc3-PTOrJaaSYSSti",
                            "staging": "pULkPU_GhLLPI_dmUlzL94f8FS6TZG65IvXVU",
                        },
                    },
                    "halleyh5": {
                        "version": "1.0.0",
                        "backupurl": backupurl,
                        "deploymentKey": {
                            "current": "production",
                            "production": "3-8v1So4lBeuqDCYzXonJiNLt3Fj3oc8f6ulOZ",
                            "staging": "NaatkyoJXw3it4CG3-6GQJvi-b2y7_R4RHHJo",
                        },
                    },
                    "uniapph5": {
                        "version": "1.0.0",
                        "backupurl": backupurl,
                        "deploymentKey": {
                            "current": "production",
                            "production": "4kf9dXW8iimbMFMzT1Xly8w0C-LqwS1F7xVlu9",
                            "staging": "a5FkqOX9uZlSysXOPrFUNqN1VR20nWae99Nu5",
                        },
                    },
                    "goatbz": {
                        "version": "1.0.0",
                        "backupurl": backupurl,
                        "deploymentKey": {
                            "current": "production",
                            "production": "QUWwhrVVTWguUhMlp9u_MydbtiEfoGuTi6RKdt",
                            "staging": "pikF7Zh-i-XixDWA9aIQl1Nul1G_IZM-vylcs",
                        },
                    },
                    "goat2": {
                        "version": "1.0.0",
                        "backupurl": backupurl,
                        "deploymentKey": {
                            "current": "production",
                            "production": "_NBzjTg2Hi76dgKK28KDXHINuou3ATAhwgwNvu",
                            "staging": "_slSX8ZCCmf_HpMd7sVO9lN9NdQkMM3mNRkmM",
                        },
                    },
                    "copernich5": {
                        "version": "1.0.0",
                        "deploymentKey": {
                            "current": "production",
                            "production": "MHo96COo_tfjZrluStRpb4H8vu8HYatJhUJ6m3",
                            "staging": "NZkAEvb3BrUMYbj3al_Gn0P4_X9BzlJgjlbgR",
                        },
                    },
                    "t20unih5": {
                        "version": "1.0.0",
                        "deploymentKey": {
                            "current": "production",
                            "production": "lurkmMKO7VW8ksOE0pMQ4DLj0fnRLEodeXtd41a",
                            "staging": "Gg1dLEaFDa3BIzkXadYNK83lKtUyM61duNB3fw",
                        },
                    },
                    "keplersph5": {
                        "version": "1.0.0",
                        "deploymentKey": {
                            "current": "production",
                            "production": "e7OedIayl7LKMEw30_OVQIOjmtGywD5uU2x_yiR",
                            "staging": "emLiXAYvihLleM7-WgHx7qV8C4QKH-yOxSxOiW",
                        },
                    },
                    "keplerseh5": {
                        "version": "1.0.0",
                        "deploymentKey": {
                            "current": "production",
                            "production": "xiLCJcXau1-LFeQ-VH-ygd_rGT-yXZIVONIEGqK",
                            "staging": "5oIeAT9YMKX-Kxjeh_S6jew-lvQwUPuTCvmnWc",
                        },
                    },
                    "eulerh5": {
                        "version": "1.0.0",
                        "deploymentKey": {
                            "current": "production",
                            "production": "vU_8bGlVcJpLoZK1p3zSHtu0NYgMstbOm4eP8wB",
                            "staging": "O9opYpHnQ2xyoXIyQJAQD0Nd0ztEkEbF2alb8i",
                        },
                    },
                    "faradaysh5": {
                        "version": "1.0.0",
                        "deploymentKey": {
                            "current": "production",
                            "production": "YfDv3lMdDThp9spiYcBeypzAxoH-dWFYzWveXY_",
                            "staging": "iU46Iq6uhWt36xOdmvJPxNTPZ8BCempGMepstf",
                        },
                    },
                    "ykeplerh5": {
                        "version": "1.0.0",
                        "deploymentKey": {
                            "current": "production",
                            "production": "NtEVsk_yIFRIPdS-rTOWjHC2eg4EiHUmNwr5Bx8",
                            "staging": "s67RZje_T5heJQpT5vghj5Fly-wXIsAaFnEB_r",
                        },
                    },
                    "galileoh5": {
                        "version": "1.0.0",
                        "deploymentKey": {
                            "current": "production",
                            "production": "dqHEJR7DgE-wOQrLGfUHHLec2rJ9P23FGX7iu5_",
                            "staging": "I8rHUQNQzbbPjHMM8P7O5V-hI3gN9Z5jMGZoGE",
                        },
                    },
                    "hmosn9h5": {
                        "version": "1.0.0",
                        "deploymentKey": {
                            "current": "production",
                            "production": "jvV8bIUNGoR9DkKEbOwA4VpZQ0Erc7YIePPa1",
                            "staging": "RuoxYw5izycQUlf2BWFLVDIger8ac7YIePPa1",
                        },
                    },
                    "vinci": {
                        "version": "1.0.0",
                        "deploymentKey": {
                            "current": "production",
                            "production": "R4zZ3MAkEFuCqInSVrPol9HgGJsyc7YIePPa1",
                            "staging": "EOxYyyV9mqyDdvb1g2XWWoi4i46ac7YIePPa1",
                        },
                    },
                },
            },
        ]

    elif code == "base_station_guide":
        data = [
            {
                "resId": "61cd0abe312d7cfc89acf608",
                "code": "base_station_guide",
                "name": "Introduction to AES base stations",  # AES基站介绍
                "description": "",
                "type": "text",
                "content": f"https://{contenturl}/pim/base_station_guide_newton_curi.html?lang=en&defaultLang=en",
            },
        ]

    elif code == "time_zone_list":
        data = [
            {
                "resId": "61a055be6533d2e6d9d8f0f1",
                "code": "time_zone_list",
                "description": "",
                "type": "json",
                "content": [
                    {"name": "New Zealand", "zone": "+12:00"},
                    {"name": "Australia", "zone": "+10:00"},
                    {"name": "South Korea, Japan", "zone": "+09:00"},
                    {"name": "China Mainland, Hong Kong, Macao, Taiwan, Singapore, Philippines, Malaysia", "zone": "+08:00"},
                    {"name": "Thailand, Indonesia, Vietnam", "zone": "+07:00"},
                    {"name": "Kazakhstan, Kyrgyzstan", "zone": "+06:00"},
                    {"name": "Tajikistan, Turkmenistan, Republic of Uzbekistan, India", "zone": "+05:00"},
                    {"name": "United Arab Emirates, Oman, Azerbaijan, Armenia", "zone": "+04:00"},
                    {"name": "Iran", "zone": "+03:30"},
                    {"name": "Belarus,Russian Federation, Kuwait, Saudi Arabia, Turkey", "zone": "+03:00"},
                    {
                        "name": (
                            "Egypt, Estonia, Bulgaria, Finland, Latvia, Lithuania,"
                            "Romania, Moldova, Cyprus, Ukraine, Greece, Israel"
                        ),
                        "zone": "+02:00",
                    },
                    {
                        "name": (
                            "Albania, Ireland, Andorra, Austria, Belgium,"
                            "Bosnia Hercegovina, Poland, Denmark, Germany, France,"
                            "Vatican City State, Netherlands, Czech Republic, Croatia,"
                            "Luxembourg, Malta, Macedonia, Monaco,Norway, Sweden,"
                            "Switzerland, Serbia, San Marino, Slovakia, Slovenia, Spain, Hungary,Italy"
                        ),
                        "zone": "+01:00",
                    },
                    {"name": "Iceland, Portugal, United Kingdom", "zone": "00:00"},
                    {"name": "Argentina, Uruguay", "zone": "-03:00"},
                    {"name": "Dominican Republic", "zone": "-04:00"},
                    {"name": "United States, Brazil, Colombia, Peru", "zone": "-05:00"},
                    {"name": "Mexico", "zone": "-06:00"},
                    {"name": "Mountain Time (US and Canada)", "zone": "-07:00"},
                    {"name": "Canada", "zone": "-08:00"},
                ],
            },
        ]

    elif code in {"yiko_record_enabled", "full_stack_yiko_entry"}:
        data = []

    elif code == "yiko_support_lang":
        data = [
            {
                "resId": "675681bca7c061000750cb05",
                "code": "yiko_support_lang",
                "name": "Languages supported by Full Stack YIKO",  # 全栈YIKO支持的语种
                "description": "Languages supported by Full Stack YIKO",  # 全栈YIKO支持的语种
                "type": "json",
                "content": {"lang": ["en"]},
            },
        ]

    if data is None:
        _LOGGER.error(f"code is not know :: {code}")
        data = []
    return response_success_v3(data)


async def _handle_service_list(request: Request) -> Response:
    """Service list."""
    try:
        area_code = request.query.get("area", bumper_isc.ECOVACS_DEFAULT_COUNTRY).lower()
        dc_code = utils.get_dc_code(area_code)
        sub_domain_1 = f"{bumper_isc.DOM_SUB_1}{bumper_isc.DOMAIN_MAIN}"
        sub_domain_2 = f"{bumper_isc.DOM_SUB_2}{bumper_isc.DOMAIN_MAIN}"
        sub_domain_3 = f"{bumper_isc.DOM_SUB_3}{bumper_isc.DOMAIN_MAIN}"

        data = {
            "account": f"users-base.{sub_domain_1}",
            "adv": f"adv-app.{sub_domain_1}",
            "dc": dc_code,
            "jmq": f"jmq-ngiot-eu.{sub_domain_2}",
            "lb": f"lbo.{bumper_isc.DOMAIN_MAIN}",
            "magw": f"api-app.{sub_domain_1}",
            "msgcloud": f"msg-eu.{bumper_isc.DOMAIN_MAIN}:5223",
            "ngiot": f"api-ngiot.{sub_domain_1}",
            "ngiotLb": f"jmq-ngiot-de.{sub_domain_3}",
            "nlp": f"iot-api-nlp.{sub_domain_1}",
            "rop": f"api-rop.{sub_domain_1}",
            "bigdata": f"bigdata-europe.{bumper_isc.DOMAIN_MAIN}",
            "base": f"api-base.{sub_domain_1}",
            "eis": f"eis-nlp.{sub_domain_1}",
            "codepush": f"codepush-base.{sub_domain_1}",
            "setApConfig": {
                "a": area_code,
                "r": bumper_isc.DOMAIN_MAIN,
                "v": "ww",
            },
        }

        return response_success_v4(data)
    except Exception:
        _LOGGER.exception(utils.default_exception_str_builder(info="during handling request"))
    raise HTTPInternalServerError


async def _handle_oauth_callback(request: Request) -> Response:
    """Oauth callback."""
    return auth_util.oauth_callback(request)


async def _handle_improve(request: Request) -> Response:
    """Improve."""
    query_did = request.query.get("did", "")
    query_mid = request.query.get("mid", "")
    query_uid = request.query.get("uid", "")
    query_lang = request.query.get("lang", "").lower()
    query_a = request.query.get("a", "")
    query_c = request.query.get("c", "")
    query_v = request.query.get("v", "")
    query_p = request.query.get("p", "")
    query_show_remark = request.query.get("show_remark", "")
    query_token = ""
    query_token_tmp: dict[str, Any] | str = request.query.get("auth", {})
    if isinstance(query_token_tmp, dict):
        query_token = query_token_tmp.get("token", "")

    domain = f"adv-app.{bumper_isc.DOM_SUB_1}{bumper_isc.DOMAIN_MAIN}"
    content = (
        f"https://{domain}/pim/productImprovePlan_ww.html?initSync=false&did={query_did}"
        f"&mid={query_mid}&uid={query_uid}&lang={query_lang}&a={query_a}&c={query_c}&v={query_v}&"
        f"p={query_p}&id=628dcf819dbd613d9ebb4fe4&ver=11.16&showRemark={query_show_remark}&remark=&token={query_token}"
    )
    return response_success_v5(
        {
            "show": False,
            "content": content,
            "remark": "",
            "updateLog": "",
        },
    )


async def _handle_improve_accept(_: Request) -> Response:
    """Improve accept."""
    return web.json_response({"code": 0})


async def _handle_improve_user_accept(_: Request) -> Response:
    """Improve accept."""
    return web.json_response({"code": 0, "data": {"accept": False}})


async def _handle_notice_home(_: Request) -> Response:
    """Notice home."""
    return response_success_v4({})


async def _handle_notice_list(_: Request) -> Response:
    """Notice list."""
    return response_success_v4({})


async def _handle_ota_firmware(_: Request) -> Response:
    """OTA firmware."""
    return web.json_response({"code": -1, "message": "No upgrades at this time"})


async def _handle_device_blacklist_check(_: Request) -> Response:
    """Device blacklist check."""
    return response_success_v3([])


def create_device_list() -> list[dict[str, Any]]:
    """Create bot device list."""
    return [
        device
        for bot in db.bot_get_all()
        if bot.get("class", "") != "" and (device := _include_product_iot_map_info(bot)) is not None
    ]


def _include_product_iot_map_info(bot: dict[str, Any]) -> dict[str, Any] | None:
    if bumper_isc.mqtt_server is None:
        msg = "'bumper.mqtt_server' is None"
        raise Exception(msg)
    result: dict[str, Any] | None = None

    for botprod in get_product_iot_map():
        if botprod["classid"] != bot["class"]:
            continue

        result = copy.deepcopy(bot)
        result.pop("mqtt_connection")
        result.pop("xmpp_connection")

        if (botprod_invent := botprod.get("product")) is not None:
            result["pid"] = botprod_invent["_id"]
            result["materialNo"] = botprod_invent["materialNo"]
            result["deviceName"] = botprod_invent["name"]
            result["model"] = botprod_invent["model"]
            result["UILogicId"] = botprod_invent["UILogicId"]
            result["ota"] = botprod_invent["ota"]
            result["icon"] = botprod_invent["iconUrl"]
            result["product_category"] = "DEEBOT" if botprod_invent["name"].startswith("DEEBOT") else "UNKNOWN"

        result["status"] = 1 if bot["mqtt_connection"] or bot["xmpp_connection"] else 0

        result["otaUpgrade"] = {}
        result["updateInfo"] = {"changeLog": "", "needUpdate": False}
        result["shareable"] = bool(bot["mqtt_connection"])
        result["sharedDevice"] = False

        # TODO: improve as non static
        result["homeId"] = bumper_isc.HOME_ID
        result["homeSort"] = 1

        if bot["mqtt_connection"]:
            result["bindTs"] = utils.get_current_time_as_millis()
            result["offmap"] = True

            # TODO: improve as non static
            result["scode"] = {
                "tmallstand": True,
                "video": True,
                "battery": True,
                "clean": True,
                "charge": True,
                "chargestate": True,
            }

            result["service"] = {
                "jmq": f"jmq-ngiot-eu.{bumper_isc.DOM_SUB_2}{bumper_isc.DOMAIN_MAIN}",
                "mqs": f"api-ngiot.{bumper_isc.DOM_SUB_1}{bumper_isc.DOMAIN_MAIN}",
            }

        # # mqtt_connection is not always set correctly, therefore workaround until fixed properly
        # for session in bumper_isc.mqtt_server.sessions:
        #     if session.client_id is not None:
        #         did = session.client_id.split("@")[0]
        #         if did == bot["did"] and session.transitions.state == "connected":
        #             result["status"] = 1
        #             break
        break  # when we found an entry this will be the only one result
    return result


async def _handle_akvs_start_watch(request: Request) -> Response:
    """AKVS start watch."""
    # TODO: check what's needed to be implemented
    # 8.219.176.88 sgp-sdk.openaccount.aliyun.com
    # a2JaaxoKXLq.iot-as-mqtt.cn-shanghai.aliyuncs.com
    utils.default_log_warn_not_impl("_handle_akvs_start_watch")
    query_did = request.query.get("did", "")
    query_auth: str | dict[str, Any] = request.query.get("auth", {})
    query_auth = json.loads(query_auth) if isinstance(query_auth, str) else query_auth
    user_id = query_auth.get("userid", "")
    resource = query_auth.get("resource", "")
    return web.json_response(
        {
            "ret": "ok",
            "region": "eu-central-1",
            "channel": f"production-{query_did}",
            "client_id": f"{user_id}-{resource}",
            "credentials": {
                "AccessKeyId": None,
                "SecretAccessKey": None,
                "SessionToken": None,
                "Expiration": "9999-12-31T00:00:00.000Z",
                "TtlSec": 3600,
            },
            "session": "de/abc1234",
            "ts": utils.get_current_time_as_millis(),
        },
    )
