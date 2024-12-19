"""Init module."""

import argparse
import asyncio
import logging
from pathlib import Path
import sys

from bumper.mqtt import helper_bot, server as server_mqtt
from bumper.utils import db, utils
from bumper.utils.log_helper import LogHelper
from bumper.utils.settings import config as bumper_isc
from bumper.web import server as server_web
from bumper.xmpp import xmpp as server_xmpp

LogHelper()

_LOGGER = logging.getLogger(__name__)


async def start() -> None:
    """Start Bumper."""
    try:
        # LogHelper()
        _LOGGER.info("Starting Bumpers...")
        await start_configuration()
        await start_service()
        _LOGGER.info("Bumper started successfully")
        await maintenance()
    except Exception:
        _LOGGER.exception("Failed to start bumper")


async def start_configuration() -> None:
    """Start Bumper configuration."""
    if bumper_isc.bumper_level == "DEBUG":
        # Set asyncio loop to debug
        asyncio.get_event_loop().set_debug(True)

    if bumper_isc.bumper_listen is None:
        _LOGGER.exception("No listen address configured!")
        raise Exception

    # Reset xmpp/mqtt to false in database for bots and clients
    db.bot_reset_connection_status()
    db.client_reset_connection_status()

    if bumper_isc.BUMPER_PROXY_MQTT is True:
        _LOGGER.info("Proxy MQTT Enabled")
    if bumper_isc.BUMPER_PROXY_WEB is True:
        _LOGGER.info("Proxy Web Enabled")

    bumper_isc.mqtt_server = server_mqtt.MQTTServer(
        [
            server_mqtt.MQTTBinding(bumper_isc.bumper_listen, bumper_isc.MQTT_LISTEN_PORT_TLS, True),
            # server_mqtt.MQTTBinding(bumper_isc.bumper_listen, bumper_isc.MQTT_LISTEN_PORT, False),
        ],
    )
    bumper_isc.mqtt_helperbot = helper_bot.MQTTHelperBot(bumper_isc.bumper_listen, bumper_isc.MQTT_LISTEN_PORT_TLS, True)
    # bumper_isc.mqtt_helperbot = helper_bot.MQTTHelperBot(bumper_isc.bumper_listen, bumper_isc.MQTT_LISTEN_PORT, False)
    bumper_isc.web_server = server_web.WebServer(
        [
            server_web.WebserverBinding(bumper_isc.bumper_listen, int(bumper_isc.WEB_SERVER_TLS_LISTEN_PORT), True),
            server_web.WebserverBinding(bumper_isc.bumper_listen, int(bumper_isc.WEB_SERVER_LISTEN_PORT), False),
        ],
        proxy_mode=bumper_isc.BUMPER_PROXY_WEB,
    )
    bumper_isc.xmpp_server = server_xmpp.XMPPServer(bumper_isc.bumper_listen, bumper_isc.XMPP_LISTEN_PORT_TLS)


async def start_service() -> None:
    """Start bumper services."""
    # Start XMPP Server
    if bumper_isc.xmpp_server is not None:
        asyncio.Task(bumper_isc.xmpp_server.start_async_server())

    # Start MQTT Server
    if bumper_isc.mqtt_server is not None:
        await bumper_isc.mqtt_server.start()
        while bumper_isc.mqtt_server.state != "started":
            _LOGGER.info("Waiting until MQTT server started...")
            await asyncio.sleep(0.1)

        # Start MQTT Helperbot
        if bumper_isc.mqtt_helperbot is not None:
            await bumper_isc.mqtt_helperbot.start()
            while bumper_isc.mqtt_helperbot.is_connected is False:
                _LOGGER.info("Waiting HelperBot connects...")
                await asyncio.sleep(0.1)

    # Start web servers
    if bumper_isc.web_server is not None:
        asyncio.Task(bumper_isc.web_server.start())


async def maintenance() -> None:
    """Run maintenance."""
    try:
        while not bumper_isc.shutting_down:
            db.revoke_expired_tokens()
            db.revoke_expired_oauths()
            await asyncio.sleep(5)
    except asyncio.CancelledError:
        pass  # Ignore the cancellation error when shutting down


async def shutdown() -> None:
    """Shutdown Bumper."""
    try:
        _LOGGER.info("Shutting down...")

        _LOGGER.info("Shutdown Maintenance...")
        bumper_isc.shutting_down = True

        if bumper_isc.mqtt_helperbot is not None:
            _LOGGER.info("Disconnect HelperBot...")
            await bumper_isc.mqtt_helperbot.disconnect()
            _LOGGER.info("HelperBot disconnect complete.")

        if bumper_isc.web_server is not None:
            _LOGGER.info("Shutdown Server 1...")
            await bumper_isc.web_server.shutdown()
            _LOGGER.info("Server 1 shutdown complete.")

        if bumper_isc.mqtt_server is not None:
            while bumper_isc.mqtt_server.state == "starting":
                _LOGGER.info("Wait until MQTT Server started until shutdown...")
                await asyncio.sleep(0.1)
            if bumper_isc.mqtt_server.state == "started":
                _LOGGER.info("Shutdown MQTT Server...")
                await bumper_isc.mqtt_server.shutdown()
                _LOGGER.info("MQTT Server shutdown complete.")

        if bumper_isc.xmpp_server is not None and bumper_isc.xmpp_server.server:
            _LOGGER.info("Shutdown XMPP Server...")
            if bumper_isc.xmpp_server.server.is_serving() is True:
                bumper_isc.xmpp_server.server.close()
                _LOGGER.info("XMPP Server close connection.")
            await bumper_isc.xmpp_server.server.wait_closed()
            _LOGGER.info("XMPP Server shutdown complete.")

        tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
        _ = [task.cancel() for task in tasks]
        await asyncio.gather(*tasks)

        asyncio.get_running_loop().stop()

    except asyncio.CancelledError:
        _LOGGER.info("Coroutine canceled!")
    except Exception:
        _LOGGER.exception(utils.default_exception_str_builder())
    finally:
        _LOGGER.info("Shutdown complete!")


def read_args(argv: list[str] | None) -> None:
    """Read arguments."""
    if not argv:
        argv = sys.argv[1:]  # Set argv to argv[1:] if not passed into main

    parser = argparse.ArgumentParser()
    parser.add_argument("--listen", type=str, default=None, help="start serving on address")
    parser.add_argument("--announce", type=str, default=None, help="announce address to bots on check-in")
    parser.add_argument("--debug_level", type=str, help="enable debug logs")
    parser.add_argument("--debug_verbose", type=int, help="enable debug logs")
    args = parser.parse_args(args=argv)

    if args.debug_level:
        bumper_isc.bumper_level = args.debug_level
    if args.debug_verbose:
        bumper_isc.bumper_verbose = args.debug_verbose
    if args.listen:
        bumper_isc.bumper_listen = args.listen
    if args.announce:
        bumper_isc.bumper_announce_ip = args.announce

    # Update logging for args updates
    LogHelper()


def main(argv: list[str] | None = None) -> None:
    """Start everything."""
    loop = asyncio.get_event_loop()

    try:
        # Check for password file?
        passwd_path = Path(bumper_isc.data_dir) / "passwd"
        if not passwd_path.exists():
            with passwd_path.open("w", encoding="utf-8"):
                pass

        # Read arguments from command line
        read_args(argv)

        if not utils.is_valid_ip(bumper_isc.bumper_listen):
            msg = "No listen address configured!"
            raise Exception(msg)

        loop.run_until_complete(start())
    except KeyboardInterrupt:
        _LOGGER.debug("Keyboard Interrupt!")
    except Exception:
        _LOGGER.critical(utils.default_exception_str_builder())
    finally:
        loop.run_until_complete(shutdown())
        if loop.is_running():
            loop.close()
