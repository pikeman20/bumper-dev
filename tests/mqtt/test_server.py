import asyncio
import ssl
from unittest import mock

from gmqtt import Client
from gmqtt.mqtt.constants import MQTTv311
import pytest
from testfixtures import LogCapture

from bumper.mqtt.server import MQTTBinding, MQTTServer, _log__helperbot_message, mqtt_proxy
from bumper.utils import db, dns
from bumper.utils.settings import config as bumper_isc
from tests import HOST, MQTT_PORT

_LOGGER_NAME = "bumper.mqtt.server"


def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


def test_log__helperbot_message():
    custom_log_message = "custom_log_message"
    topic = "topic"
    data = "data"
    with LogCapture() as log:
        _log__helperbot_message(custom_log_message, topic, data)
        log.check_present(
            (
                f"{_LOGGER_NAME}.messages",
                "DEBUG",
                f"{custom_log_message} :: Topic: {topic} :: Message: {data}",
            ),
            order_matters=False,
        )


@pytest.mark.usefixtures("clean_database")
@pytest.mark.parametrize("proxy", [False, True])
async def test_mqttserver(proxy: bool):
    bumper_isc.BUMPER_PROXY_MQTT = proxy

    mqtt_server = MQTTServer(MQTTBinding(HOST, MQTT_PORT, True), password_file="tests/_test_files/passwd", allow_anonymous=True)

    await mqtt_server.start()

    try:
        # Test client connect
        db.user_add("user_123")  # Add user to db
        db.client_add("user_123", "ecouser.net", "resource_123")  # Add client to db

        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        client = Client("user_123@ecouser.net/resource_123")
        await client.connect(HOST, MQTT_PORT, ssl=ssl_ctx, version=MQTTv311)  # type: ignore
        assert client.is_connected
        await client.disconnect()
        assert not client.is_connected

        # Test fake_bot connect
        client = Client("bot_serial@ls1ok3/wC3g")
        await client.connect(HOST, MQTT_PORT, ssl=ssl_ctx, version=MQTTv311)  # type: ignore
        assert client.is_connected
        await client.disconnect()

        # Test file auth client connect
        client = Client("test-file-auth")
        client.set_auth_credentials("test-client", "abc123!")
        await client.connect(HOST, MQTT_PORT, ssl=ssl_ctx, version=MQTTv311)  # type: ignore
        assert client.is_connected
        await client.disconnect()
        assert not client.is_connected

        # bad password
        with LogCapture() as log:
            client.set_auth_credentials("test-client", "notvalid!")
            await client.connect(HOST, MQTT_PORT, ssl=ssl_ctx, version=MQTTv311)  # type: ignore
            await client.disconnect()

            log.check_present(
                (
                    _LOGGER_NAME,
                    "INFO",
                    "File Authentication Failed :: Username: test-client - ClientID: test-file-auth",
                ),
                order_matters=False,
            )
            log.clear()

            # no username in file
            client.set_auth_credentials("test-client-noexist", "notvalid!")
            await client.connect(HOST, MQTT_PORT, ssl=ssl_ctx, version=MQTTv311)  # type: ignore
            await client.disconnect()

            log.check_present(
                (
                    _LOGGER_NAME,
                    "INFO",
                    "File Authentication Failed :: No Entry for :: Username: test-client-noexist - ClientID: test-file-auth",
                ),
                order_matters=False,
            )
            log.clear()

            # Test proxy
            if proxy:
                dns.resolve = mock.MagicMock(return_value=async_return("127.0.0.1"))
                mqtt_proxy.ProxyClient.connect = mock.MagicMock(return_value=async_return(True))

                client = Client("user_123@ls1ok3/wC3g")
                client.set_auth_credentials("user_123", "abc123!")
                await client.connect(HOST, MQTT_PORT, ssl=ssl_ctx, version=MQTTv311)  # type: ignore
                assert client.is_connected

                await client.disconnect()

                log.check_present(
                    (
                        _LOGGER_NAME,
                        "INFO",
                        "Bumper Authentication Success :: Bot :: SN: user_123 :: DID: user_123 :: Class: ls1ok3",
                    ),
                    order_matters=False,
                )

                log.check_present(
                    (
                        f"{_LOGGER_NAME}.proxy",
                        "INFO",
                        "MQTT Proxy Mode :: Using server 127.0.0.1 for client user_123@ls1ok3/wC3g",
                    ),
                    order_matters=False,
                )

    finally:
        await mqtt_server.shutdown()


@pytest.mark.usefixtures("clean_database")
@pytest.mark.parametrize("proxy", [False])
async def test_mqttserver_subscribe(proxy: bool):
    with LogCapture() as log:
        # NOTE: for proxy test subscription solution how to connect needs to be checked
        bumper_isc.BUMPER_PROXY_MQTT = proxy
        if proxy:
            dns.resolve = mock.MagicMock(return_value=async_return("127.0.0.1"))

        mqtt_server = MQTTServer(
            MQTTBinding(HOST, MQTT_PORT, True), password_file="tests/_test_files/passwd", allow_anonymous=True
        )

        try:
            await mqtt_server.start()

            # Test client connect
            db.user_add("user_123")  # Add user to db
            db.client_add("user_123", "ecouser.net", "resource_123")  # Add client to db

            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
            client = Client("user_123@ls1ok3/wC3g")
            client.set_auth_credentials("user_123", "abc123!")
            await client.connect(HOST, MQTT_PORT, ssl=ssl_ctx, version=MQTTv311)  # type: ignore
            assert client.is_connected
            log.clear()
            client.subscribe("iot/atr/+/+/+/+/+")
            await asyncio.sleep(0.1)

            await client.disconnect()
            assert not client.is_connected

            log.check_present(
                (
                    _LOGGER_NAME,
                    "DEBUG",
                    "MQTT Broker :: New MQTT Topic Subscription :: Client: user_123@ls1ok3/wC3g :: Topic: iot/atr/+/+/+/+/+",
                ),
                order_matters=False,
            )

        finally:
            await mqtt_server.shutdown()


async def test_mqttserver_no_file_auth():
    with LogCapture() as log:
        mqtt_server = MQTTServer(MQTTBinding(HOST, MQTT_PORT, True), password_file="tests/_test_files/passwd-notfound")
        await mqtt_server.start()
        try:
            log.check_present(
                (
                    _LOGGER_NAME,
                    "WARNING",
                    "Password file tests/_test_files/passwd-notfound not found",
                ),
                order_matters=False,
            )
        finally:
            await mqtt_server.shutdown()


async def test_mqttserver_default_pw_file_double_start():
    with LogCapture() as log:
        mqtt_server = MQTTServer(MQTTBinding(HOST, MQTT_PORT, True))
        try:
            await mqtt_server.start()
            log.check_present(
                (
                    _LOGGER_NAME,
                    "INFO",
                    f"Starting MQTT Server at {HOST}:{MQTT_PORT}",
                ),
                order_matters=False,
            )

            log.clear()

            await mqtt_server.start()
            log.check_present(
                (
                    _LOGGER_NAME,
                    "INFO",
                    "MQTT Server is still running, stop first for a restart!",
                ),
                order_matters=False,
            )
        finally:
            await mqtt_server.shutdown()


async def test_mqttserver_shutdown():
    with LogCapture() as log:
        mqtt_server = MQTTServer(MQTTBinding(HOST, MQTT_PORT, True))
        try:
            await mqtt_server.start()

            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
            client = Client("user_123@ecouser.net/resource_123")
            await client.connect(HOST, MQTT_PORT, ssl=ssl_ctx, version=MQTTv311)  # type: ignore
            assert client.is_connected

        finally:
            log.clear()
            assert len(mqtt_server.handlers) > 0
            await mqtt_server.shutdown()
            assert len(mqtt_server.handlers) == 0

            log.check_present(
                (
                    f"{_LOGGER_NAME}.broker",
                    "INFO",
                    "Broker closed",
                ),
                order_matters=False,
            )

            log.clear()
            await mqtt_server.shutdown()
            log.check_present(
                (
                    _LOGGER_NAME,
                    "WARNING",
                    f"MQTT server is not in a valid state for shutdown. Current state: {mqtt_server.state}",
                ),
                order_matters=False,
            )
