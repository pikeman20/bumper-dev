"""Helper bot module."""
import asyncio
import json
import logging
import ssl
from collections.abc import MutableMapping
from typing import Any, cast

from cachetools import TTLCache
from gmqtt import Client as MQTTClient
from gmqtt import Subscription
from gmqtt.mqtt.constants import MQTTv311

from bumper.utils import utils

_LOGGER = logging.getLogger("helperbot")
HELPER_BOT_CLIENT_ID = "helperbot@bumper/helperbot"


class CommandDto:
    """Command DTO."""

    def __init__(self, payload_type: str) -> None:
        """Command DTO init."""
        self._payload_type = payload_type
        self._event = asyncio.Event()
        self._response: str | bytes

    async def wait_for_response(self) -> str | dict[str, Any]:
        """Wait for the response to be received."""
        await self._event.wait()
        if self._payload_type == "j":
            return cast(dict[str, Any], json.loads(self._response))
        return str(self._response)

    def add_response(self, response: str | bytes) -> None:
        """Add received response."""
        self._response = response
        self._event.set()


class MQTTHelperBot:
    """Helper bot, which converts commands from the rest api to mqtt ones."""

    def __init__(self, host: str, port: int, use_ssl: bool, timeout: float = 60):
        """MQTT helper bot init."""
        self._commands: MutableMapping[str, CommandDto] = TTLCache(maxsize=timeout * 60, ttl=timeout * 1.1)
        self._host = host
        self._port = port
        self._use_ssl = use_ssl
        self._timeout = timeout
        self._client = MQTTClient(HELPER_BOT_CLIENT_ID)
        # self._client.set_config({"check_hostname": False, "reconnect_retries": 20})

        # pylint: disable=unused-argument
        async def _on_message(client: MQTTClient, topic: str, payload: bytes, qos: int, properties: dict) -> None:
            try:
                decoded_payload = payload.decode()
                _LOGGER.debug("Got message: topic={topic}; payload={decoded_payload};")
                topic_split = topic.split("/")
                data_decoded = str(decoded_payload)
                if topic_split[10] in self._commands:
                    self._commands[topic_split[10]].add_response(data_decoded)
            except Exception as e:
                _LOGGER.error(utils.default_exception_str_builder(e, "during handling message"), exc_info=True)

        self._client.on_message = _on_message

    @property
    def is_connected(self) -> bool:
        """Return True if client is connected successfully."""
        return bool(self._client.is_connected)

    async def start(self) -> None:
        """Connect and subscribe helper bot."""
        try:
            if self.is_connected:
                return

            ssl_ctx: bool | ssl.SSLContext = self._use_ssl
            if ssl_ctx is True:
                ssl_ctx = ssl.create_default_context()
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl.CERT_NONE
            # bumper.ca_cert
            await self._client.connect(self._host, self._port, ssl=ssl_ctx, version=MQTTv311)
            self._client.subscribe(Subscription("iot/p2p/+/+/+/+/helperbot/bumper/helperbot/+/+/+"))
        except Exception as e:
            _LOGGER.exception(utils.default_exception_str_builder(e, "during startup"), exc_info=True)
            raise

    async def _wait_for_resp(self, command_dto: CommandDto, request_id: str) -> dict[str, Any]:
        try:
            payload = await asyncio.wait_for(command_dto.wait_for_response(), timeout=self._timeout)
            return {"id": request_id, "ret": "ok", "resp": payload}
        except TimeoutError:
            _LOGGER.debug("wait_for_resp timeout reached")
        except asyncio.CancelledError:
            _LOGGER.debug("wait_for_resp cancelled by asyncio", exc_info=True)
        except Exception as e:
            _LOGGER.exception(utils.default_exception_str_builder(e, None), exc_info=True)

        return {
            "id": request_id,
            "errno": 500,
            "ret": "fail",
            "debug": "wait for response timed out",
        }

    async def send_command(self, cmdjson: dict[str, Any], request_id: str) -> dict[str, Any]:
        """Send command over MQTT."""
        if not self.is_connected:
            await self.start()

        try:
            topic = (
                f"iot/p2p/{cmdjson['cmdName']}/helperbot/bumper/helperbot/{cmdjson['toId']}/"
                f"{cmdjson['toType']}/{cmdjson['toRes']}/q/{request_id}/{cmdjson['payloadType']}"
            )

            if cmdjson["payloadType"] == "j":
                payload = json.dumps(cmdjson["payload"])
            else:
                payload = str(cmdjson["payload"])

            command_dto = CommandDto(cmdjson["payloadType"])
            self._commands[request_id] = command_dto

            _LOGGER.debug(f"Sending message: topic={topic}; payload={payload};")
            self.publish(topic, payload.encode())

            resp = await self._wait_for_resp(command_dto, request_id)
            return resp
        except Exception as e:
            _LOGGER.exception(f"Could not send command :: {e}", exc_info=True)
            return {
                "id": request_id,
                "errno": 500,
                "ret": "fail",
                "debug": "exception occurred please check bumper logs",
            }
        finally:
            self._commands.pop(request_id, None)

    def publish(self, topic: str, data: bytes) -> None:
        """Publish message."""
        self._client.publish(topic, data)

    async def disconnect(self) -> None:
        """Disconnect client."""
        if self.is_connected:
            await self._client.disconnect()
