"""Pim product plugin module."""

from collections.abc import Iterable
import json
import logging
from pathlib import Path
from typing import Any

import aiofiles
from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import utils
from bumper.web.images import get_bot_image
from bumper.web.plugins import WebserverPlugin
from bumper.web.response_utils import response_success_v3, response_success_v4

from . import get_product_iot_map

_LOGGER = logging.getLogger(__name__)


class ProductPlugin(WebserverPlugin):
    """Product plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/product/getProductIotMap",
                _handle_get_product_iot_map,
            ),
            web.route(
                "*",
                "/product/getConfignetAll",
                _handle_get_config_net_all,
            ),
            web.route(
                "*",
                "/product/getConfigGroups",
                _handle_get_config_groups,
            ),
            web.route(
                "POST",
                "/product/software/config/batch",
                _handle_config_batch,
            ),
            web.route(
                "POST",
                "/product/getShareInfo",
                _handle_get_share_info,
            ),
            web.route(
                "GET",
                "/product/image",
                get_bot_image,
            ),
        ]


async def _handle_get_product_iot_map(_: Request) -> Response:
    """Get product iot map."""
    try:
        return response_success_v4(get_product_iot_map())

    except Exception:
        _LOGGER.exception(utils.default_exception_str_builder(info="during handling request"))
    raise HTTPInternalServerError


async def _handle_get_config_net_all(_: Request) -> Response:
    """Get config net all."""
    try:
        async with aiofiles.open(Path(__file__).parent / "configNetAllResponse.json", encoding="utf-8") as file:
            file_content = await file.read()
            return web.json_response(json.loads(file_content))
    except Exception:
        _LOGGER.exception(utils.default_exception_str_builder(info="during handling request"))
    raise HTTPInternalServerError


async def _handle_get_config_groups(_: Request) -> Response:
    """Get config groups."""
    try:
        async with aiofiles.open(Path(__file__).parent / "configGroupsResponse.json", encoding="utf-8") as file:
            file_content = await file.read()
            return web.json_response(json.loads(file_content))
    except Exception:
        _LOGGER.exception(utils.default_exception_str_builder(info="during handling request"))
    raise HTTPInternalServerError


async def _handle_config_batch(request: Request) -> Response:
    """Handle product config batch."""
    try:
        async with aiofiles.open(Path(__file__).parent / "productConfigBatch.json", encoding="utf-8") as file:
            file_content = await file.read()
            product_config_batch: list[dict[str, Any]] = json.loads(file_content)

        json_body = json.loads(await request.text())
        data = []
        for pid in json_body.get("pids", []):
            for product_config in product_config_batch:
                if pid == product_config.get("pid", ""):
                    data.append(product_config)
                    continue

            # not found in product_config_batch
            # some devices don't have any product configuration
            data.append({"cfg": {}, "pid": pid})

        return response_success_v3(data=data, code=200)
    except Exception:
        _LOGGER.exception(utils.default_exception_str_builder(info="during handling request"))
    raise HTTPInternalServerError


async def _handle_get_share_info(request: Request) -> Response:
    """Get share info."""
    try:
        json_body = json.loads(await request.text())
        scene = json_body.get("scene")
        _LOGGER.debug(f"Share info :: {scene}")
        return response_success_v4([])
    except Exception:
        _LOGGER.exception(utils.default_exception_str_builder(info="during handling request"))
    raise HTTPInternalServerError
