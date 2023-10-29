"""Auth util module."""
import json
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

_LOGGER = logging.getLogger(__name__)


def _generate_token(user_id: str) -> str:
    """Generate token."""
    token = uuid.uuid4().hex
    db.user_add_token(user_id, token)
    return token


def _generate_auth_code(user_id: str, country_code: str, token: str) -> str:
    """Generate auth token."""
    tmp_auth_code = f"{country_code}_{uuid.uuid4().hex}"
    db.user_add_authcode(user_id, token, tmp_auth_code)
    return tmp_auth_code


async def login(request: Request) -> Response:
    """Perform login."""
    try:
        user_dev_id = request.match_info.get("devid", "")
        country_code = request.match_info.get("country", "us")
        app_type = request.match_info.get("apptype", "")
        _LOGGER.info(f"Client with devid {user_dev_id} attempting login")
        if bumper_isc.USE_AUTH:
            if user_dev_id != "":
                # Performing basic "auth" using devid, super insecure
                user = db.user_by_device_id(user_dev_id)
                if user is None:
                    _LOGGER.warning(f"No user found for {user_dev_id}")
                else:
                    if "checkLogin" in request.path:
                        return web.json_response(_check_token(app_type, country_code, user, request.query["accessToken"])[1])

                    # Deactivate old tokens and authcodes
                    db.user_revoke_expired_tokens(user["userid"])

                    return web.json_response(
                        {
                            "code": models.API_ERRORS[models.RETURN_API_SUCCESS],
                            "data": _get_login_details(app_type, country_code, user, _generate_token(user["userid"])),
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

        return web.json_response(_auth_any(user_dev_id, app_type, country_code, request))
    except Exception as e:
        _LOGGER.exception(utils.default_exception_str_builder(e, None), exc_info=True)
    raise HTTPInternalServerError


async def get_auth_code(request: Request) -> Response:
    """Get auth code."""
    try:
        user_dev_id = request.match_info.get("devid", None)  # Ecovacs
        if not user_dev_id:
            user_dev_id = request.query.get("deviceId", None)  # Ecovacs Home
        access_token = request.query.get("accessToken")

        if user_dev_id is not None and access_token is not None:
            user = db.user_by_device_id(user_dev_id)
            if user is None:
                _LOGGER.warning(f"No user found for {user_dev_id}")
            else:
                token = db.user_get_token(user["userid"], access_token)
                if token is not None:
                    if "authcode" in token:
                        auth_code = token.get("authcode")
                    else:
                        auth_code = _generate_auth_code(
                            user["userid"],
                            request.match_info.get("country", "us"),
                            access_token,
                        )

                    return plugins.get_success_response(
                        {
                            "authCode": auth_code,
                            "ecovacsUid": request.query.get("uid"),
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


async def get_auth_code2(request: Request) -> dict[str, Any]:
    """Get auth code2."""
    try:
        post_body = json.loads(await request.text())
        user_id = post_body.get("auth", {}).get("userid")
        access_token = post_body.get("auth", {}).get("token")

        body = {
            "code": models.ERR_TOKEN_INVALID,
            "data": None,
            "msg": "当前密码错误",
            "time": utils.get_current_time_as_millis(),
        }

        if user_id is not None and access_token is not None:
            user = db.user_get(user_id)
            if user is None:
                _LOGGER.warning(f"No user found for {user_id}")
            else:
                token = db.user_get_token(user_id, access_token)
                if token is not None:
                    auth_code = None
                    if "authcode" in token:
                        auth_code = token.get("authcode")
                    else:
                        auth_code = _generate_auth_code(
                            user["userid"],
                            request.match_info.get("country", "us"),
                            access_token,
                        )

                    body = {
                        "code": auth_code,
                        "result": "ok",
                        "todo": "result",
                    }

        return body
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
    user_dev_id = devid
    country_code = country
    user = db.user_by_device_id(user_dev_id)
    bots = db.bot_get_all()

    if user is None:
        db.user_add("tmpuser")  # Add a new user
        tmp = db.user_get("tmpuser")
        assert tmp
        user = tmp

    token = _generate_token(user["userid"])
    db.user_add_device(user["userid"], user_dev_id)

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
