"""Webserver utils module."""

from typing import Any

from aiohttp import web
from aiohttp.web_response import Response

from bumper.utils import utils
from bumper.web import models

# ******************************************************************************


def response_success_v1(data: Any) -> Response:
    """Response success v1."""
    return web.json_response(
        {
            "code": models.RETURN_API_SUCCESS,
            "data": data,
            "msg": "The operation was successful.",
            "success": True,
            "time": utils.get_current_time_as_millis(),
        },
    )


def response_success_v2(data: Any, data_key: str = "data") -> Response:
    """Response success v2."""
    return web.json_response(
        {
            data_key: data,
            "ret": "ok",
            "todo": "result",
        },
    )


def response_success_v3(data: Any, code: int = 0, data_key: str = "data") -> Response:
    """Response success v3."""
    return web.json_response(
        {
            "code": code,
            data_key: data,
            "message": "success",
        },
    )


def response_success_v4(data: Any, data_key: str = "data") -> Response:
    """Response success v4."""
    return web.json_response(
        {
            "code": 0,
            data_key: data,
            "ret": "ok",
            "todo": "result",
        },
    )


def response_success_v5(data: Any, code: int = 0, data_key: str = "data") -> Response:
    """Response success v5."""
    return web.json_response(
        {
            "code": code,
            data_key: data,
        },
    )


def response_success_v6(data: Any, code: int = 0) -> Response:
    """Response success v6."""
    return web.json_response(
        {
            "code": code,
            "data": data,
            "message": "success",
            "success": True,
        },
    )


def response_success_v7(data: Any, code: int = 0) -> Response:
    """Response success v7."""
    return web.json_response(
        {
            "code": code,
            "data": data,
            "msg": "success",
        },
    )


def response_success_v8() -> Response:
    """Response success v8."""
    return web.json_response({"code": 0, "message": "success"})


def response_success_v9() -> Response:
    """Response success v9."""
    return web.json_response({"result": "ok", "todo": "result"})


# ******************************************************************************


def response_error_v1(msg: str = "Parameter error. Please try again later", code: str = models.ERR_COMMON) -> Response:
    """Response error v1."""
    return web.json_response(
        {
            "code": code,
            "msg": msg,
            "time": utils.get_current_time_as_millis(),
        },
    )


def response_error_v2(msg: str = "Parameter error. Please try again later", code: str = models.ERR_COMMON) -> Response:
    """Response error v2."""
    return web.json_response(
        {
            "errno": code,
            "error": msg,
            "result": "fail",
            "todo": "result",
        },
    )


def response_error_v3(msg: str = "Parameter error. Please try again later", code: str = models.ERR_COMMON) -> Response:
    """Response error v3."""
    return web.json_response(
        {
            "errno": code,
            "error": msg,
            "result": "fail",
            "todo": "result",
        },
    )


def response_error_v4(msg: str = "Parameter error. Please try again later") -> Response:
    """Response error v4."""
    return web.json_response(
        {
            "todo": "result",
            "ret": "fail",
            "errno": msg,
        },
    )


def response_error_v5() -> Response:
    """Response error v5."""
    return web.json_response(
        {
            "todo": "result",
            "ret": "fail",
            "err": 2004,
            "errno": 2004,
            "code": 2004,
        },
    )


def response_error_v6(debug: str, error: str = "Error request, unknown todo") -> Response:
    """Response error v6."""
    return web.json_response(
        {
            "todo": "result",
            "result": "fail",
            "errno": 1,
            "error": error,
            "debug": debug,
        },
    )


def response_error_v7(errno: int = 1, error: str = "unknown") -> Response:
    """Response error v7."""
    return web.json_response(
        {
            "ret": "fail",
            "errno": errno,
            "error": error,
        },
    )


# ******************************************************************************


def get_success_response(data: Any) -> Response:
    """Get success response with provided data."""
    return web.json_response(
        {
            "code": models.RETURN_API_SUCCESS,
            "data": data,
            "msg": "The operation was successful",
            "success": True,
            "time": utils.get_current_time_as_millis(),
        },
    )


# def get_error_response_v2() -> Response:
#     """Get error response."""
#     random_id = "".join(random.sample(string.ascii_letters, 6))
#     return web.json_response(
#         {
#             "id": random_id,
#             "errno": models.ERR_COMMON,
#             "result": "fail",
#             "ret": "fail",
#             "todo": "result",
#         }
#     )
