"""Helper bot module."""

import asyncio
import json
import logging
import ssl
from typing import TYPE_CHECKING, Any

from cachetools import TTLCache
from gmqtt import Client as MQTTClient, Subscription
from gmqtt.mqtt.constants import MQTTv311

from bumper.mqtt.handle_atr import clean_log
from bumper.utils import utils

if TYPE_CHECKING:
    from collections.abc import MutableMapping

_LOGGER = logging.getLogger(__name__)
HELPER_BOT_CLIENT_ID = "helperbot@bumper/helperbot"


class MQTTHelperBot:
    """Helper bot, which converts commands from the rest api to mqtt ones."""

    def __init__(self, host: str, port: int, use_ssl: bool, timeout: float = 60) -> None:
        """MQTT helper bot init."""
        self._host = host
        self._port = port
        self._use_ssl = use_ssl
        self._timeout = timeout

        self._commands: MutableMapping[str, CommandDto] = TTLCache(maxsize=timeout * 60, ttl=timeout * 1.1)

        self._client = MQTTClient(client_id=HELPER_BOT_CLIENT_ID)
        self._client.on_message = self._on_message
        self._client.on_connect = self._on_connect

    @property
    def is_connected(self) -> bool:
        """Return True if client is connected successfully."""
        return bool(self._client.is_connected)

    async def start(self) -> None:
        """Connect helper bot."""
        try:
            if self.is_connected is False:
                _LOGGER.info("Staring Helper Bot...")

                ssl_ctx: ssl.SSLContext | bool = False
                if self._use_ssl is True:
                    ssl_ctx = ssl.create_default_context()
                    ssl_ctx.check_hostname = False
                    ssl_ctx.verify_mode = ssl.CERT_NONE

                await self._client.connect(self._host, self._port, ssl=ssl_ctx, version=MQTTv311)
        except Exception:
            _LOGGER.exception(utils.default_exception_str_builder(info="during startup"))
            raise

    async def disconnect(self) -> None:
        """Disconnect helper bot."""
        if self.is_connected is True:
            _LOGGER.info("Disconnecting Helper Bot...")
            await self._client.disconnect()

    async def send_command(self, cmdjson: dict[str, Any], request_id: str) -> dict[str, Any]:
        """Send command over MQTT."""
        try:
            if self.is_connected is False:
                await self.start()

            payload_type = cmdjson.get("payloadType", "x")
            payload = cmdjson.get("payload")

            topic = (
                f"iot/p2p/{cmdjson['cmdName']}/helperbot/bumper/helperbot/{cmdjson['toId']}/"
                f"{cmdjson['toType']}/{cmdjson['toRes']}/q/{request_id}/{payload_type}"
            )

            payload = json.dumps(payload) if payload_type == "j" else str(payload)

            command_dto = CommandDto(payload_type)
            self._commands[request_id] = command_dto

            _LOGGER.debug(f"Sending message :: topic={topic} :: payload={payload}")
            self.publish(topic, payload)

            return await self._wait_for_resp(command_dto, request_id)
        except Exception:
            _LOGGER.exception("Could not send command")
            return {
                "id": request_id,
                "errno": 500,
                "ret": "fail",
                "debug": "exception occurred please check bumper logs",
            }
        finally:
            self._commands.pop(request_id, None)

    def publish(self, topic: str, payload: str) -> None:
        """Publish message."""
        self._client.publish(topic, payload.encode())

    async def _wait_for_resp(self, command_dto: "CommandDto", request_id: str) -> dict[str, Any]:
        """Wait for response."""
        try:
            return {
                "id": request_id,
                "ret": "ok",
                "resp": await asyncio.wait_for(command_dto.wait_for_response(), timeout=self._timeout),
            }
        except TimeoutError:
            _LOGGER.debug("wait_for_resp timeout reached")
        except asyncio.CancelledError:
            _LOGGER.debug("wait_for_resp cancelled by asyncio", exc_info=True)
        except Exception:
            _LOGGER.exception(utils.default_exception_str_builder(info="during wait for response"))
        return {
            "id": request_id,
            "errno": 500,
            "ret": "fail",
            "debug": "wait for response timed out",
        }

    def _on_connect(self, *_: Any) -> None:
        _LOGGER.debug("HelperBot connected and will subscribe")
        self._client.subscribe(
            (
                Subscription("iot/p2p/+/+/+/+/helperbot/bumper/helperbot/+/+/+"),
                Subscription("iot/atr/+/+/+/+/+"),
            ),
        )

    def _on_message(self, _client: MQTTClient, topic: str, payload: bytes, _qos: int, _properties: dict[str, Any]) -> None:
        try:
            decoded_payload: bytes | bytearray | str | memoryview = payload
            if isinstance(decoded_payload, bytearray | bytes):
                decoded_payload = decoded_payload.decode("utf-8", errors="replace")
            if isinstance(decoded_payload, memoryview):
                decoded_payload = decoded_payload.tobytes().decode("utf-8")

            _LOGGER.debug(f"Got message :: topic={topic} :: payload={decoded_payload}")
            topic_split = topic.split("/")
            if topic_split[1] == "p2p" and topic_split[10] in self._commands:
                self._commands[topic_split[10]].add_response(decoded_payload)
            elif topic_split[1] == "atr" and topic_split[2] in ("onStats", "reportStats"):
                clean_log(did=topic_split[3], rid=topic_split[5], payload=decoded_payload)
        except Exception:
            _LOGGER.exception(utils.default_exception_str_builder(info="on message"))
            raise


class CommandDto:
    """Command DTO."""

    def __init__(self, payload_type: str) -> None:
        """Command DTO init."""
        self._payload_type = payload_type
        self._event = asyncio.Event()
        self._response: str | bytes | None = None

    async def wait_for_response(self) -> str | dict[str, Any]:
        """Wait for the response to be received."""
        await self._event.wait()
        if self._payload_type == "j" and self._response is not None:
            res = json.loads(self._response)
            if isinstance(res, dict):
                return res
        return str(self._response)

    def add_response(self, response: str | bytes) -> None:
        """Add received response."""
        self._response = response
        self._event.set()
