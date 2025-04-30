"""Pim Event Detail plugin module."""

from collections.abc import Iterable
import logging

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.web.plugins import WebserverPlugin

_LOGGER = logging.getLogger(__name__)


class EventDetailPlugin(WebserverPlugin):
    """Event Detail plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/eventdetail.html",
                _handle_eventdetail,
            ),
        ]


async def _handle_eventdetail(_: Request) -> Response:
    """Event Detail."""
    html_content = """
    <div style="font-family: Arial, sans-serif; margin: 2rem auto; padding: 1.5em;
    border: 2px solid #b22222; border-radius: 8px; background-color: #fff0f0; font-size: 2rem; max-width: 52rem;">
    <h2 style="color: #b22222; text-align: center;">🚨 Event: Dustbin Drama Detected</h2>
    <p>
        <strong>Status:</strong>
        Your robot has bravely battled dust... and lost. The bin is full. Full of dust. Full of dreams.
    </p>

    <h3>Recommended Action</h3>
    <ol>
        <li>Locate your robot. It may be hiding in shame.</li>
        <li>Open the dustbin compartment (you can do it — believe in yourself).</li>
        <li>Empty contents into an appropriate container. Bonus points for not sneezing.</li>
        <li>Give the bin a gentle shake or rinse. Whisper words of encouragement.</li>
        <li>Reinsert bin. Pat robot. Tell it “you’re clean now.”</li>
    </ol>

    <h3>Optional Rituals</h3>
    <ul>
        <li>Light a candle for the lost crumbs.</li>
        <li>Perform the sacred "turn it off and on again" dance.</li>
        <li>Contemplate the impermanence of dust and life itself.</li>
    </ul>

    <p style="text-align: center; font-style: italic; margin-top: 1.5em;">
        This message will self-destruct after your floor sparkles again. 🧼✨
    </p>
    </div>
    """
    return web.Response(text=html_content, content_type="text/html")
