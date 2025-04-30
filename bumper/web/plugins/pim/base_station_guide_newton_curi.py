"""Base station guide newton curi plugin module."""

from collections.abc import Iterable
import logging

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_routedef import AbstractRouteDef

from bumper.web.images import get_bot_image
from bumper.web.plugins import WebserverPlugin

_LOGGER = logging.getLogger(__name__)


class EventDetailPlugin(WebserverPlugin):
    """Base station guide newton curi plugin."""

    @property
    def routes(self) -> Iterable[AbstractRouteDef]:
        """Plugin routes."""
        return [
            web.route(
                "*",
                "/base_station_guide_newton_curi.html",
                _handle_base_station_guide_newton_curi,
            ),
            web.route(
                "*",
                "/images/{id}",
                get_bot_image,
            ),
        ]


async def _handle_base_station_guide_newton_curi(_: Request) -> Response:
    """Handle Base station guide newton curi."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8" />
    <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" name="viewport" />
    <title>Base Station Guide</title>
    <style>
        html, body {
        height: 100%;
        margin: 0;
        padding: 0;
        overflow: auto;
        font-family: Arial, sans-serif;
        background-color: #fff;
        }

        .container {
        width: 90%;
        max-width: 52rem;
        margin: 0 auto;
        padding: 1.5em 1em 4em;
        box-sizing: border-box;
        }

        h1 {
        font-size: 18px;
        color: #253746;
        padding: 10px 0;
        }

        hr {
        border: none;
        border-top: 1px solid #eef1f5;
        margin: 20px 0;
        }

        .subheading {
        display: flex;
        align-items: center;
        margin: 1em 0 0.5em 0;
        }

        .seq {
        border-radius: 50%;
        width: 22px;
        height: 22px;
        background-color: #253746;
        color: white;
        text-align: center;
        line-height: 22px;
        margin-right: 10px;
        font-size: 14px;
        }

        .illustration, .illustration-second {
        font-size: 14px;
        color: #253746;
        }

        .illustration-second {
        margin-left: 32px;
        display: block;
        margin-top: 4px;
        }

        img.img-fit {
        max-width: 100%;
        height: auto;
        margin: 20px 0;
        display: block;
        }
    </style>
    </head>
    <body>
    <div class="container">
        <h1>1. Empty Station</h1>
        <img class="img-fit" src="/pim/images/base_station_introduction_newton_curi_en.png" alt="Base Station Overview" />

        <hr />

        <h1>2. Dust Bag</h1>

        <div class="subheading">
        <div class="seq">1</div>
        <span class="illustration">Dispose the Dust Bag</span>
        </div>
        <p class="illustration-second">
        Hold the Handle to lift out the Dust Bag, which can effectively prevent dust leakage.
        </p>
        <img class="img-fit" src="/pim/images/dust_bag1_newton_curi.png" alt="Dispose Dust Bag" />

        <div class="subheading">
        <div class="seq">2</div>
        <span class="illustration">Clean the Dust Bag Cabin with a dry cloth</span>
        </div>
        <p class="illustration-second">and put a new Dust Bag in</p>
        <img class="img-fit" src="/pim/images/dust_bag2_newton_curi.png" alt="Clean and Replace Bag" />

        <div class="subheading">
        <div class="seq">3</div>
        <span class="illustration">Close the Dust Bag Cabin</span>
        </div>
        <img class="img-fit" src="/pim/images/dust_bag3_newton_curi.png" alt="Close the Cabin" />
    </div>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type="text/html")
