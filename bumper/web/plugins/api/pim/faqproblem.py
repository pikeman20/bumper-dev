"""Pim FAQ problem plugin module."""

from collections.abc import Iterable
import logging

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.web.plugins import WebserverPlugin

_LOGGER = logging.getLogger(__name__)


class FaqProblemPlugin(WebserverPlugin):
    """FAQ problem plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/faqproblem.html",
                _handle_faqproblem,
            ),
        ]


async def _handle_faqproblem(_: Request) -> Response:
    """FAQ problem."""
    html_content = """
    <div style="font-family: Arial, sans-serif; margin: 2rem auto; padding: 1.5em;
    border: 2px solid #444; border-radius: 8px; background-color: #fffbe6; font-size: 2rem; max-width: 52rem;">
    <h2 style="text-align: center;">Bumper FAQ: Frequently Annoying Questions 🤖❓</h2>
    <h3>Q: My robot just spun in a circle, beeped twice, and then sulked under the couch. Why?</h3>
    <p>A: It probably sensed your energy. Or it detected a ghost. Hard to say. Try rebooting... or burning sage.</p>

    <h3>Q: Does Bumper work offline?</h3>
    <p>A: Yes! In fact, Bumper *only* works offline. If it starts working online, please unplug everything and run.</p>

    <h3>Q: Is my data safe?</h3>
    <p>A: Safer than your group chat. Bumper stores everything locally, where only you (and maybe your cat) can see it.</p>

    <h3>Q: I yelled at the robot and now it won't clean. Help?</h3>
    <p>A: Apologize gently. Maybe offer it a microfiber cloth or a firmware update as a peace offering.</p>

    <h3>Q: How do I contact support?</h3>
    <p>A: You are the support. Check the logs, the docs, or the stars. And if all else fails... just turn it off and on again.</p>

    <p style="text-align: center; font-style: italic; margin-top: 2em;">
        Still have questions? Perfect. So do we. But somehow, things mostly work. 🎉
    </p>
    </div>
    """
    return web.Response(text=html_content, content_type="text/html")
