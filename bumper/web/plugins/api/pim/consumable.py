"""Pim consumable plugin module."""
from collections.abc import Iterable
import logging

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import utils
from bumper.web.plugins import WebserverPlugin
from bumper.web.response_utils import response_success_v7

_LOGGER = logging.getLogger(__name__)


class ConsumablePlugin(WebserverPlugin):
    """Consumable plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/consumable/getPurchaseUrl",
                _handle_get_purchase_url,
            ),
        ]


async def _handle_get_purchase_url(_: Request) -> Response:
    """Get purchas url."""
    try:
        desc_side_brush = (
            "Dual Side Brushes can collect dust and send it to the Main Brush, so as to better clean the corners."
            " In the process of cleaning, the Side Brush may get entangled with hair. Please remove the hair with"
            " the multi-function cleaning tool promptly. To get the best cleaning experience, it is recommended to change"
            " the Side Brush every 150 hours of work or less.  If you wish to purchase our special multi-function"
            " cleaning tool, visit our store online or in the ECOVACS HOME App."
        )
        desc_main_brush = (
            "Main Brush is the main cleaning component of DEEBOT, which can pick up debris on the floor and send it"
            " to the Dust Bin. In the process of cleaning, the Main Brush may be tangled with hair. Please remove the"
            " hair with the multi-function cleaning tool promptly. To get the best cleaning experience, it is recommended"
            " to change the Main Brush every 300 hours of cleaning or less. If you wish to purchase our special multi-function"
            " cleaning tool, visit our store online or in the ECOVACS HOME App."
        )
        desc_main_brush = (
            "Main Brush is the main cleaning component of DEEBOT, which can pick up debris on the floor and send it"
            " to the Dust Bin. In the process of cleaning, the Main Brush may be tangled with hair. Please remove the"
            " hair with the multi-function cleaning tool promptly. To get the best cleaning experience, it is recommended"
            " to change the Main Brush every 300 hours of cleaning or less. If you wish to purchase our special"
            " multi-function cleaning tool, visit our store online or in the ECOVACS HOME App."
        )
        desc_filter = (
            "When DEEBOT is cleaning, the filter can effectively prevent the dust in the Dust Bin from escaping."
            " With an increase in cleaning duration, dust may gradually block the filter and affect cleaning efficiency."
            " Rinse the filter with water and dry it thoroughly every two weeks. It is recommended to change the filter"
            " every 120 hours of cleaning or less."
        )
        desc_dust_bag = (
            "The Dust Bag is an accessory for the Station; it is recommended to use it with a station that supports"
            " Auto-Empty feature. When cleaning is complete, DEEBOT will return to the Station and automatically empty"
            " the Dust Bin, saving you time and effort. To get the best cleaning experience, it is recommended to"
            " regularly replace the Dust Bag and clean the Dust Bag Cabin once a month."
        )
        desc_disposable_cleaning_cloth = (
            "DEEBOT is compatible with a Disposable Cleaning Cloth for mopping, which is easy to apply and dispose"
            " of, does not need to be washed, and prevents the breeding of bacteria from prolonged storage of a damp"
            " cloth.\nTo get the best cleaning experience, it is recommended to dispose of the Disposable Cleaning"
            " Cloth every time after mopping."
        )
        desc_other_components = (
            "1. DEEBOT Maintenance: After DEEBOT has been working for a while, components will be contaminated with"
            " dust, hair and other debris, which will reduce cleaning efficiency. It is recommended to wipe up the dust"
            " with a dry cloth and remove the hair with the multi-function cleaning tool every 30 hours of cleaning"
            " or less. For more information, please refer to the instruction manual.  If you wish to purchase our"
            " special multi-function cleaning tool, visit our store online or in the ECOVACS HOME App."
        )
        desc_air_freshener_capsule = (
            "DEEBOT can diffuse fragrance via Air Freshener while cleaning. To get the best air freshening experience,"
            " it is recommended to change the Air Freshening Capsule every 60 hours or less."
        )

        return response_success_v7(
            [
                {
                    "desc": {
                        "content": desc_side_brush,
                        "images": [
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65a53a95a16082ef62b75",
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65a5370c881b5d965ebd6",
                        ],
                    },
                    "icon": "https://portal-ww.ecouser.net/api/pim/file/get/61a5f036ed50344bd5b52819",
                    "id": "6284c3badd78026bbb57ffba",  # pragma: allowlist secret
                    "name": "Side Brush",
                    "paramType": "URL",
                    "sort": 0,
                    "type": "sideBrush",
                    "url": "https://www.ecovacs.com/us/deebot-winbot-accessories/D-KT01-0017",
                },
                {
                    "desc": {
                        "content": desc_main_brush,
                        "images": [
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65a6470c881359c65ebd7",
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65a649d1b811cd1574677",
                        ],
                    },
                    "icon": "https://portal-ww.ecouser.net/api/pim/file/get/61a5f0a45afd254c7a5c6959",
                    "id": "6284c3bddd78024c6a57ffbc",  # pragma: allowlist secret
                    "name": "Main Brush",
                    "paramType": "URL",
                    "sort": 1,
                    "type": "brush",
                    "url": "https://www.ecovacs.com/us/deebot-winbot-accessories/D-KT01-0017",
                },
                {
                    "desc": {
                        "content": desc_main_brush,
                        "images": [
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65a6470c881359c65ebd7",
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65a649d1b811cd1574677",
                        ],
                    },
                    "icon": "https://portal-ww.ecouser.net/api/pim/file/get/61a5f0a45afd254c7a5c6959",
                    "id": "62df495e176a4d3d8780acdc",  # pragma: allowlist secret
                    "name": "Main Brush",
                    "paramType": "URL",
                    "sort": 1,
                    "type": "brush",
                    "url": "",
                },
                {
                    "desc": {
                        "content": desc_filter,
                        "images": [
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65a77843b5ac787b74e36",
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65a77fd39e41ee3132ded",
                        ],
                    },
                    "icon": "https://portal-ww.ecouser.net/api/pim/file/get/61a5f0e472e3052928c1160a",
                    "id": "62df4998176a4dfae880acde",  # pragma: allowlist secret
                    "name": "Filter",
                    "paramType": "URL",
                    "sort": 2,
                    "type": "heap",
                    "url": "https://www.ecovacs.com/us/deebot-winbot-accessories/ACCESSORY-Airfilter-T10X1-Series",
                },
                {
                    "desc": {
                        "content": desc_dust_bag,
                        "images": [
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65a889ee4d3820c02cd71",
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65a8870c88178a665ebd8",
                        ],
                    },
                    "icon": "https://portal-ww.ecouser.net/api/pim/file/get/61a5f1fded5034391bb5281a",
                    "id": "6284c3c3dd78025dd557ffc1",  # pragma: allowlist secret
                    "name": "Dust Bag",
                    "paramType": "URL",
                    "sort": 3,
                    "type": "dustBag",
                    "url": "",
                },
                {
                    "desc": {
                        "content": desc_disposable_cleaning_cloth,
                        "images": [
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d659c89ee4d39fc802cd6d",
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d659c8843b5a8597b74e35",
                        ],
                    },
                    "icon": "https://portal-ww.ecouser.net/api/pim/file/get/61d6592cfe802336b9d12e7d",
                    "id": "6284c3c6dd7802847257ffc3",  # pragma: allowlist secret
                    "name": "Disposable Cleaning Cloth",
                    "paramType": "URL",
                    "sort": 5,
                    "type": "oneTimeCloth",
                    "url": "",
                },
                {
                    "desc": {
                        "content": desc_other_components,
                        "images": [
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65aa4fd39e4647a132dee",
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65aa470c88112d965ebd9",
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65aa4fe80236a34d12e7f",
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65aa4fd39e448e0132def",
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65aa4843b5a5049b74e37",
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65aa470c881c28865ebda",
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d65aa470c8814e1c65ebdb",
                            "https://portal-ww.ecouser.net/api/pim/file/get/629471d79dbd618f3fbb501e",
                        ],
                    },
                    "icon": "https://portal-ww.ecouser.net/api/pim/file/get/61a5f38172e305764bc1160c",
                    "id": "6284c3c9dd78023a6057ffc5",  # pragma: allowlist secret
                    "name": "Other Components",
                    "paramType": "URL",
                    "sort": 6,
                    "type": "unitCare",
                    "url": "",
                },
                {
                    "desc": {
                        "content": desc_air_freshener_capsule,
                        "images": [
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d659fa9ee4d3154402cd6e",
                            "https://portal-ww.ecouser.net/api/pim/file/get/61d659fa9ee4d345dd02cd6f",
                        ],
                    },
                    "icon": "https://portal-ww.ecouser.net/api/pim/file/get/61d659e6fd39e48ab8132dec",
                    "id": "6284c3ccdd78024ea157ffc7",  # pragma: allowlist secret
                    "name": "Air Freshener Capsule",
                    "paramType": "URL",
                    "sort": 7,
                    "type": "dModule",
                    "url": "",
                },
            ]
        )
    except Exception as e:
        _LOGGER.exception(utils.default_exception_str_builder(e, "during handling request"))
    raise HTTPInternalServerError
