"""OS mall plugin module."""
from collections.abc import Iterable

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from ... import WebserverPlugin, get_success_response
from . import BASE_URL


class OsMallPlugin(WebserverPlugin):
    """OS mall plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                f"{BASE_URL}osmall/getCountryConfig",
                _handle_get_country_config,
            ),
            web.route(
                "*",
                f"{BASE_URL}osmall/proxy/my/get-user-center-coupon-list",
                _handle_get_user_center_coupon_list,
            ),
            web.route(
                "*",
                f"{BASE_URL}osmall/index/getLayout",
                _handle_get_layout,
            ),
            web.route(
                "*",
                f"{BASE_URL}osmall/proxy/cart/get-count",
                _handle_get_count,
            ),
            web.route(
                "*",
                f"{BASE_URL}osmall/proxy/v2/web/benefit/get-benefits",
                _handle_get_benefits,
            ),
            web.route(
                "*",
                f"{BASE_URL}osmall/proxy/order/list",
                _handle_list,
            ),
        ]


async def _handle_get_country_config(request: Request) -> Response:
    country_code = request.match_info.get("country", "EN").upper()
    return get_success_response(
        {
            "defaultLang": country_code,
            "openNative": "Y",
            "wapMallUrl": "",
        }
    )


async def _handle_get_user_center_coupon_list(_: Request) -> Response:
    return get_success_response([])


async def _handle_get_layout(_: Request) -> Response:
    return get_success_response(
        {
            "bgColorNo": "",
            "bgImgUrlBenefit": "",
            "bgImgUrlNv": "",
            "indexId": "20220929111910_9f988dd276fec8ecaedb5f83bbe227fb",
            "indexItemList": [
                {"moduleType": "TOP_BENEFIT"},
                {"moduleType": "TOP_BANNER"},
                {"moduleType": "GOODS_CATEGORY"},
                {"moduleType": "ACCESSORY_RECOMMEND"},
                {"moduleType": "GOODS_RECOMMEND"},
                {"moduleType": "OFFICIAL_BENEFIT"},
                {"moduleType": "SAFE_PAYMENT"},
            ],
        }
    )


async def _handle_get_count(_: Request) -> Response:
    return get_success_response({"item_count": 0.0})


async def _handle_get_benefits(_: Request) -> Response:
    return get_success_response([])


async def _handle_list(_: Request) -> Response:
    return get_success_response(
        {
            "list": [],
            "page_data": {
                "current_page": 1.0,
                "list_count": 10.0,
                "total_count": 0.0,
                "total_page": 0.0,
            },
        }
    )
