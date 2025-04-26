"""New-Perm plugin module."""

from collections.abc import Iterable
import logging

from aiohttp import web
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.utils import db, utils
from bumper.web.plugins import WebserverPlugin
from bumper.web.response_utils import response_success_v3

_LOGGER = logging.getLogger(__name__)


class NewPermPlugin(WebserverPlugin):
    """New-Perm plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "POST",
                "/new-perm/token/sst/issue",
                _handle_sst_issue,
            ),
        ]


async def _handle_sst_issue(request: Request) -> Response:
    # TODO: check what's needed to be implemented
    utils.default_log_warn_not_impl("_handle_sst_issue")
    try:
        token: str | None = None
        access_token = _extract_bearer_token(request)
        if (user_id := db.user_id_by_token(access_token)) and (token_doc := db.user_get_token_v2(user_id)):
            token = token_doc.get("token")

        return response_success_v3(
            msg_key="msg",
            msg="ok",
            data={"data": {"token": token}},
        )
    except Exception:
        _LOGGER.exception(utils.default_exception_str_builder(info="during handling request"))
    raise HTTPInternalServerError


def _extract_bearer_token(request: Request) -> str:
    """Pull a token out of 'Authorization: Bearer <token>'.

    Raises HTTPUnauthorized if missing or malformed.
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise web.HTTPUnauthorized(text="Missing or invalid Authorization header")
    return auth.split(" ", 1)[1].strip()
