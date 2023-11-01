"""Webserver utils module."""
import random
import string
from typing import Any

from aiohttp import web
from aiohttp.web_response import Response

from bumper.utils import utils
from bumper.web import models


def get_success_response(data: Any) -> Response:
    """Get success response with provided data."""
    body = {
        "code": models.RETURN_API_SUCCESS,
        "data": data,
        "msg": "The operation was successful",
        "success": True,
        "time": utils.get_current_time_as_millis(),
    }
    return web.json_response(body)


def get_error_response(msg: str = "The operation was not successful", code: str = models.ERR_TOKEN_INVALID) -> Response:
    """Get error response with provided data."""
    body = {
        "code": code,
        "data": None,
        "msg": msg,
        "success": False,
        "time": utils.get_current_time_as_millis(),
    }
    return web.json_response(body)


def get_success_response_v2(data: Any) -> Response:
    """Get success response with provided data."""
    body = {
        "code": 0,
        "data": data,
        "ret": "ok",
        "todo": "result",
    }
    return web.json_response(body)


def get_success_response_v3(data: Any) -> Response:
    """Get success response with provided data."""
    body = {
        "code": 0,
        "data": data,
        "message": "success",
        "success": True,
    }
    return web.json_response(body)


def get_error_response_v2() -> Response:
    """Get error response with provided data."""
    random_id = "".join(random.sample(string.ascii_letters, 6))
    body = {
        "id": random_id,
        "errno": models.ERR_COMMON,
        "result": "fail",
        "ret": "fail",
        "todo": "result",
    }
    return web.json_response(body)
