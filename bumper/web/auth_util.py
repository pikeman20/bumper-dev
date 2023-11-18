"""Auth util module."""
import hashlib
import json
import logging
from typing import Any
import uuid

from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from bumper.utils import db, utils
from bumper.utils.settings import config as bumper_isc
from bumper.web import models
from bumper.web.response_utils import (
    response_error_v1,
    response_error_v2,
    response_error_v4,
    response_success_v1,
    response_success_v2,
)

_LOGGER = logging.getLogger(__name__)

GENERATE_AUTH_CODE_V1 = 1
GENERATE_AUTH_CODE_V2 = 2

# ******************************************************************************
#
# AUTH UTILS
#
# ******************************************************************************


async def login(request: Request) -> Response:
    """Perform login."""
    try:
        uid: str | None = None
        access_token: str | None = None
        check = False
        if "checkLogin" in request.path:
            uid = request.query.get("uid")
            access_token = request.query.get("accessToken")
            check = True
        else:
            if (account := request.query.get("account")) is not None:
                uid = _generate_uid(account)
            _ = request.query.get("encryptPwd")

        device_id = request.match_info.get("devid")
        country_code = request.match_info.get("country", bumper_isc.ECOVACS_DEFAULT_COUNTRY)
        app_type = request.match_info.get("apptype")

        if bumper_isc.USE_AUTH:
            _LOGGER.info(f"Client with devid {device_id} attempting login")
            if device_id is not None and app_type is not None:
                # Performing basic "auth" using devid, super insecure
                user = db.user_by_device_id(device_id)
                if user is None:
                    _LOGGER.warning(f"No user found for {device_id}")
                else:
                    if "checkLogin" in request.path:
                        return _check_token(app_type, country_code, user, request.query["accessToken"])[1]
                    # Deactivate old tokens and authcodes
                    db.user_revoke_expired_tokens(user.userid)
                    return response_success_v1(_get_login_details(app_type, country_code, user, _generate_token(user.userid)))
            return response_error_v1(msg="Parameter error. Please try again later.", code=models.ERR_TOKEN_INVALID)

        if device_id is not None and app_type is not None:
            return _auth_any(uid, access_token, device_id, app_type, country_code, check)
    except Exception as e:
        _LOGGER.exception(utils.default_exception_str_builder(e, "during login"), exc_info=True)
    raise HTTPInternalServerError


async def get_auth_code(request: Request) -> Response:
    """Get auth code."""
    try:
        device_id = request.match_info.get("devid")  # Ecovacs
        if device_id is None:
            device_id = request.query.get("deviceId")  # Ecovacs Home
        access_token = request.query.get("accessToken")

        if device_id is not None and access_token is not None:
            user = db.user_by_device_id(device_id)
            if user is None:
                _LOGGER.warning(f"No user found for {device_id}")
            else:
                auth_code = _get_auth_code(
                    user.userid, access_token, request.match_info.get("country", bumper_isc.ECOVACS_DEFAULT_COUNTRY)
                )
                if auth_code is not None:
                    return response_success_v1({"authCode": auth_code, "ecovacsUid": user.userid})

        return response_error_v1(msg="Interface Authentication Failure", code=models.ERR_TOKEN_INVALID)
    except Exception as e:
        _LOGGER.exception(utils.default_exception_str_builder(e, "during get auth code"), exc_info=True)
    raise HTTPInternalServerError


async def get_auth_code_v2(request: Request) -> Response:
    """Get auth code v2."""
    try:
        post_body = json.loads(await request.text())
        user_id = post_body.get("auth", {}).get("userid")
        access_token = post_body.get("auth", {}).get("token")

        if user_id is not None and access_token is not None:
            user = db.user_by_user_id(user_id)
            if user is None:
                _LOGGER.warning(f"No user found for {user_id}")
            else:
                auth_code = _get_auth_code(
                    user.userid, access_token, request.match_info.get("country", bumper_isc.ECOVACS_DEFAULT_COUNTRY), 2
                )
                if auth_code is not None:
                    return response_success_v2(auth_code, "code")

        return response_error_v2(msg="auth error", code="1004")
    except Exception as e:
        _LOGGER.exception(utils.default_exception_str_builder(e, "during get auth code v2"), exc_info=True)
    raise HTTPInternalServerError


def _get_auth_code(
    user_id: str, access_token: str, country: str = bumper_isc.ECOVACS_DEFAULT_COUNTRY, version: int = GENERATE_AUTH_CODE_V1
) -> str | None:
    """Get auth code."""
    auth_code: str | None = None

    # version 2 ignore the access_token, because current it was the easiest workaround ^^
    if version == GENERATE_AUTH_CODE_V2:
        if (token := db.user_get_token_v2(user_id)) is not None:
            if (auth_code := token.get("authcode")) is None:
                auth_code = _generate_auth_code(user_id, country, access_token, 2)
            return auth_code

    elif (token := db.user_get_token(user_id, access_token)) is not None:
        if (auth_code := token.get("authcode")) is None:
            auth_code = _generate_auth_code(user_id, country, access_token)
        return auth_code

    return None


def _check_token(apptype: str, country_code: str, user: models.BumperUser, token: str) -> tuple[bool, Response]:
    if db.check_token(user.userid, token):
        return (True, response_success_v1(_get_login_details(apptype, country_code, user, token)))
    return (False, response_error_v1(msg="Parameter error. Please try again later.", code=models.ERR_TOKEN_INVALID))


def _auth_any(
    uid: str | None, access_token: str | None, device_id: str, apptype: str, country_code: str, check: bool
) -> Response:
    if uid is None:
        uid = _generate_uid("tmpuser")

    body = response_error_v1(msg="Parameter error. Please try again later.", code=models.ERR_TOKEN_INVALID)
    user = db.user_by_user_id(uid)

    # anyway if it is a login or only checklogin
    # we will create a user if not exists and generated always a token, to be always authenticated
    if user is None:
        # Add a new user
        db.user_add(uid)
        user = db.user_by_user_id(uid)

    if user is not None:
        _auth_any_clean(user, device_id)
        token = _generate_token(user.userid)
        body = response_success_v1(_get_login_details(apptype, country_code, user, token))

        # If request was to check a token
        if check is True and access_token is not None:
            # NOTE: half used, if false the response will be true from above login
            (success, result) = _check_token(apptype, country_code, user, access_token)
            if success is True:
                body = result

    return body


def _auth_any_clean(user: models.BumperUser, device_id: str) -> None:
    # Add current used device to user
    db.user_add_device(user.userid, device_id)
    # Add all known bots to the user
    bots = db.bot_get_all()
    for bot in bots:
        if "did" in bot:
            db.user_add_bot(user.userid, bot["did"])
        else:
            _LOGGER.error(f"No DID for bot :: {bot}")

    # Deactivate old tokens and authcodes
    db.user_revoke_expired_tokens(user.userid)


def _get_login_details(apptype: str, country_code: str, user: models.BumperUser, token: str) -> dict[str, Any]:
    details: dict[str, Any] = {
        "accessToken": token,
        "email": "null@null.com",
        "isNew": None,
        "loginName": user.userid,
        "mobile": None,
        "ucUid": user.userid,
        "uid": user.userid,
        "username": user.username,
        "country": country_code,
    }

    if "global_" in apptype:
        details.update({"ucUid": details["uid"], "loginName": details["username"], "mobile": None})

    return details


# ******************************************************************************
#
# OAUTH UTILS
#
# ******************************************************************************


def oauth_callback(request: Request) -> Response:
    """Oauth callback."""
    try:
        if (auth_code := request.query.get("code")) is None:
            return response_error_v4()
        if (token := db.token_by_auth_code(auth_code)) is None:
            return response_error_v4()
        if (user := token.get("userid")) is None:
            return response_error_v4()
        if (oauth := db.user_add_oauth(user)) is None:
            return response_error_v4()

        return response_success_v2(oauth.to_response())
    except Exception as e:
        _LOGGER.exception(utils.default_exception_str_builder(e, "during handling oauth callback"), exc_info=True)
    raise HTTPInternalServerError


# ******************************************************************************
#
# HELPER UTILS
#
# ******************************************************************************


def _generate_uid(email: str) -> str:
    """Generate an uid from a given E-Mail."""
    hash_object = hashlib.sha256()
    hash_object.update(email.encode("utf-8"))
    return hash_object.hexdigest()[:20]


def _generate_token(user_id: str) -> str:
    """Generate new token and add to DB."""
    token = uuid.uuid4().hex
    db.user_add_token(user_id, token)
    return token


def _generate_auth_code(user_id: str, country_code: str, token: str, version: int = GENERATE_AUTH_CODE_V1) -> str:
    """Generate new auth token and add to DB."""
    tmp_auth_code = f"{country_code}_{uuid.uuid4().hex}"
    if version == GENERATE_AUTH_CODE_V1:
        db.user_add_auth_code(user_id, token, tmp_auth_code)
    elif version == GENERATE_AUTH_CODE_V2:
        db.user_add_auth_code_v2(user_id, tmp_auth_code)
    return tmp_auth_code


# async def get_auth_info(request: Request) -> tuple[tuple | None, tuple | None]:
#     """Get auth info from requests."""
#     try:
#         auth_keys = ["accessToken", "token", "user_token"]
#         user_keys = ["uid", "userid"]

#         token: tuple | None = None
#         user: tuple | None = None

#         # Search in headers or query for credentials
#         for key in auth_keys:
#             auth_value = request.headers.get(key) or request.query.get(key)
#             if auth_value:
#                 token = (key, auth_value)

#         # Search in headers or query for user info
#         for key in user_keys:
#             user_value = request.headers.get(key) or request.query.get(key)
#             if user_value:
#                 user = (key, user_value)

#         # Search in JSON body
#         try:
#             if token is None and user is None:
#                 token = _find_keys_in_json(await request.json(), auth_keys)
#                 user = _find_keys_in_json(await request.json(), user_keys)
#         except Exception as e:
#             _LOGGER.warning(utils.default_exception_str_builder(e, "during handle json decoding"))

#         return (user, token)
#     except Exception as e:
#         _LOGGER.warning(utils.default_exception_str_builder(e, "during auth info gather"))
#     return (None, None)


# def _find_keys_in_json(data: dict | list | None, keys_to_find: list[str]) -> tuple | None:
#     if isinstance(data, dict):
#         for key, value in data.items():
#             if key in keys_to_find:
#                 return (key, value)
#             if isinstance(value, (dict, list)):
#                 result = _find_keys_in_json(value, keys_to_find)
#                 if result:
#                     return result
#     elif isinstance(data, list):
#         for item in data:
#             result = _find_keys_in_json(item, keys_to_find)
#             if result:
#                 return result
#     return None
