import asyncio
import ssl

from gmqtt import Client
from gmqtt.mqtt.constants import MQTTv311
import pytest

from bumper.mqtt.helper_bot import MQTTHelperBot
from bumper.mqtt.server import MQTTBinding, MQTTServer
from bumper.utils.settings import config as bumper_isc
from bumper.web.server import WebServer, WebserverBinding
from tests import HOST, MQTT_PORT, WEBSERVER_PORT


@pytest.fixture
async def mqtt_server():
    mqtt_server = MQTTServer(MQTTBinding(HOST, MQTT_PORT, True), password_file="tests/passwd")

    await mqtt_server.start()
    bumper_isc.mqtt_server = mqtt_server
    while mqtt_server.state != "started":
        await asyncio.sleep(0.1)

    yield mqtt_server

    await mqtt_server.shutdown()


@pytest.fixture
async def mqtt_client(mqtt_server: MQTTServer):
    assert mqtt_server.state == "started"

    client = Client("helperbot@bumper/test")
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    await client.connect(HOST, MQTT_PORT, ssl=ssl_ctx, version=MQTTv311)  # type: ignore

    yield client

    await client.disconnect()


@pytest.fixture
async def helper_bot(mqtt_server: MQTTServer):
    assert mqtt_server.state == "started"

    helper_bot = MQTTHelperBot(HOST, MQTT_PORT, True, 0.1)
    bumper_isc.mqtt_helperbot = helper_bot
    await helper_bot.start()
    assert helper_bot.is_connected

    yield helper_bot

    await helper_bot.disconnect()


@pytest.fixture
async def webserver_client(aiohttp_client):
    webserver = WebServer(WebserverBinding(HOST, WEBSERVER_PORT, False), False)
    client = await aiohttp_client(webserver._app)

    yield client

    await client.close()
