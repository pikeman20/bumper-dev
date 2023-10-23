"""Auth util module."""
import logging
import uuid
from typing import Any

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from bumper.utils import db, utils
from bumper.utils.settings import config as bumper_isc
from bumper.web import models, plugins

_LOGGER = logging.getLogger("web_auth_util")


def _generate_token(user: dict[str, Any]) -> str:
    """Generate token."""
    token = uuid.uuid4().hex
    db.user_add_token(user["userid"], token)
    return token


def _generate_auth_code(user: dict[str, Any], country_code: str, token: str) -> str:
    """Generate auth token."""
    tmp_auth_code = f"{country_code}_{uuid.uuid4().hex}"
    db.user_add_authcode(user["userid"], token, tmp_auth_code)
    return tmp_auth_code


async def login(request: Request) -> Response:
    """Perform login."""
    try:
        user_devid = request.match_info.get("devid", "")
        country_code = request.match_info.get("country", "us")
        app_type = request.match_info.get("apptype", "")
        _LOGGER.info(f"Client with devid {user_devid} attempting login")
        if bumper_isc.USE_AUTH:
            if user_devid != "":
                # Performing basic "auth" using devid, super insecure
                user = db.user_by_device_id(user_devid)
                if user:
                    if "checkLogin" in request.path:
                        return web.json_response(_check_token(app_type, country_code, user, request.query["accessToken"])[1])

                    # Deactivate old tokens and authcodes
                    db.user_revoke_expired_tokens(user["userid"])

                    return web.json_response(
                        {
                            "code": models.API_ERRORS[models.RETURN_API_SUCCESS],
                            "data": _get_login_details(app_type, country_code, user, _generate_token(user)),
                            "msg": "操作成功",
                            "time": utils.get_current_time_as_millis(),
                        }
                    )

            return web.json_response(
                {
                    "code": models.ERR_USER_NOT_ACTIVATED,
                    "data": None,
                    "msg": "当前密码错误",
                    "time": utils.get_current_time_as_millis(),
                }
            )

        return web.json_response(_auth_any(user_devid, app_type, country_code, request))
    except Exception as e:
        _LOGGER.exception(utils.default_exception_str_builder(e, None), exc_info=True)
    raise HTTPInternalServerError


async def get_auth_code(request: Request) -> Response:
    """Get auth code."""
    try:  # pylint: disable=too-many-nested-blocks
        user_devid = request.match_info.get("devid", None)  # Ecovacs
        if not user_devid:
            user_devid = request.query["deviceId"]  # Ecovacs Home

        if user_devid:
            user = db.user_by_device_id(user_devid)
            if user:
                if "accessToken" in request.query:
                    token = db.user_get_token(user["userid"], request.query["accessToken"])
                    if token:
                        if "authcode" in token:
                            auth_code = token["authcode"]
                        else:
                            auth_code = _generate_auth_code(
                                user,
                                request.match_info.get("country", "us"),
                                request.query["accessToken"],
                            )

                        return plugins.get_success_response(
                            {
                                "authCode": auth_code,
                                "ecovacsUid": request.query["uid"],
                            }
                        )

        body = {
            "code": models.ERR_TOKEN_INVALID,
            "data": None,
            "msg": "当前密码错误",
            "time": utils.get_current_time_as_millis(),
        }

        return web.json_response(body)
    except Exception as e:
        _LOGGER.error(utils.default_exception_str_builder(e, None), exc_info=True)
    raise HTTPInternalServerError


def _check_token(apptype: str, country_code: str, user: dict[str, Any], token: str) -> tuple[bool, dict[str, Any]]:
    if db.check_token(user["userid"], token):
        return (
            True,
            {
                "code": models.RETURN_API_SUCCESS,
                "data": _get_login_details(apptype, country_code, user, token),
                "msg": "操作成功",
                "time": utils.get_current_time_as_millis(),
            },
        )

    return (
        False,
        {
            "code": models.ERR_TOKEN_INVALID,
            "data": None,
            "msg": "当前密码错误",
            "time": utils.get_current_time_as_millis(),
        },
    )


def _auth_any(devid: str, apptype: str, country: str, request: Request) -> dict[str, Any]:
    user_devid = devid
    country_code = country
    user = db.user_by_device_id(user_devid)
    bots = db.bot_get_all()

    if not user:
        db.user_add("tmpuser")  # Add a new user
        tmp = db.user_get("tmpuser")
        assert tmp
        user = tmp

    token = _generate_token(user)
    db.user_add_device(user["userid"], user_devid)

    for bot in bots:  # Add all bots to the user
        if "did" in bot:
            db.user_add_bot(user["userid"], bot["did"])
        else:
            _LOGGER.error(f"No DID for bot :: {bot}")

    if "checkLogin" in request.path:  # If request was to check a token do so
        (success, body) = _check_token(apptype, country_code, user, request.query["accessToken"])
        if success:
            return body

    # Deactivate old tokens and authcodes
    db.user_revoke_expired_tokens(user["userid"])

    return {
        "code": models.RETURN_API_SUCCESS,
        "data": _get_login_details(apptype, country_code, user, token),
        "msg": "操作成功",
        "time": utils.get_current_time_as_millis(),
    }


def _get_login_details(apptype: str, country_code: str, user: dict[str, Any], token: str) -> dict[str, Any]:
    details: dict[str, Any] = {
        "accessToken": token,
        "email": "null@null.com",
        "isNew": None,
        "loginName": f"fuid_{user['userid']}",
        "mobile": None,
        "ucUid": f"fuid_{user['userid']}",
        "uid": f"fuid_{user['userid']}",
        "username": f"fusername_{user['userid']}",
        "country": country_code,
    }

    if "global_" in apptype:
        details.update({"ucUid": details["uid"], "loginName": details["username"], "mobile": None})

    return details
