"""Confi module."""
import os
import socket
from typing import TYPE_CHECKING, Optional

from bumper.utils import utils

if TYPE_CHECKING:
    from bumper.mqtt.helper_bot import MQTTHelperBot
    from bumper.mqtt.server import MQTTServer
    from bumper.web.server import WebServer
    from bumper.xmpp.xmpp import XMPPServer


class Config:
    """Config class."""

    # ww: 52.53.84.66 | eu: 3.68.172.231
    ECOVACS_UPDATE_SERVER: str = "3.68.172.231"
    ECOVACS_UPDATE_SERVER_PORT: int = 8005

    # os.environ['PYTHONASYNCIODEBUG'] = '1' # Uncomment to enable ASYNCIODEBUG
    bumper_dir: str = f"{os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))}/../"

    # Set defaults from environment variables first
    # Folders
    data_dir = os.environ.get("BUMPER_DATA") or os.path.join(bumper_dir, "data")
    os.makedirs(data_dir, exist_ok=True)  # Ensure data directory exists or create
    certs_dir = os.environ.get("BUMPER_CERTS") or os.path.join(bumper_dir, "certs")
    os.makedirs(certs_dir, exist_ok=True)  # Ensure data directory exists or create

    # Certs
    ca_cert = os.environ.get("BUMPER_CA") or os.path.join(certs_dir, "ca.crt")
    server_cert = os.environ.get("BUMPER_CERT") or os.path.join(certs_dir, "bumper.crt")
    server_key = os.environ.get("BUMPER_KEY") or os.path.join(certs_dir, "bumper.key")

    # Listeners
    bumper_listen: str | None = os.environ.get("BUMPER_LISTEN", socket.gethostbyname(socket.gethostname()))
    bumper_announce_ip: str | None = os.environ.get("BUMPER_ANNOUNCE_IP", bumper_listen)

    # Logging
    bumper_level: str = (os.environ.get("BUMPER_DEBUG_LEVEL") or "INFO").upper()
    bumper_verbose: int = int(os.environ.get("BUMPER_DEBUG_VERBOSE") or 1)
    DEBUG_LOGGING_API_REQUEST: bool = utils.strtobool(os.environ.get("DEBUG_LOGGING_API_REQUEST")) or False
    DEBUG_LOGGING_API_REQUEST_MISSING: bool = utils.strtobool(os.environ.get("DEBUG_LOGGING_API_REQUEST_MISSING")) or False
    DEBUG_LOGGING_XMPP_REQUEST: bool = utils.strtobool(os.environ.get("DEBUG_LOGGING_XMPP_REQUEST")) or False
    DEBUG_LOGGING_XMPP_REQUEST_REFACTOR: bool = utils.strtobool(os.environ.get("DEBUG_LOGGING_XMPP_REQUEST_REFACTOR")) or False
    DEBUG_LOGGING_XMPP_RESPONSE: bool = utils.strtobool(os.environ.get("DEBUG_LOGGING_XMPP_RESPONSE")) or False
    DEBUG_LOGGING_API_ROUTE: bool = utils.strtobool(os.environ.get("DEBUG_LOGGING_API_ROUTE")) or False

    # Other
    USE_AUTH: bool = False
    TOKEN_VALIDITY_SECONDS: int = 3600  # 1 hour
    OAUTH_VALIDITY_DAYS: int = 15
    BUMPER_PROXY_MQTT: bool = utils.strtobool(os.environ.get("BUMPER_PROXY_MQTT")) or False
    BUMPER_PROXY_WEB: bool = utils.strtobool(os.environ.get("BUMPER_PROXY_WEB")) or False

    # Proxy
    PROXY_NAMESERVER: list[str] = ["1.1.1.1", "8.8.8.8"]
    PROXY_MQTT_DOMAIN: str = "mq-ww.ecouser.net"

    # Ports
    WEB_SERVER_TLS_LISTEN_PORT: int = int(os.environ.get("WEB_SERVER_HTTPS_PORT") or 443)
    WEB_SERVER_LISTEN_PORT: int = 8007
    MQTT_LISTEN_PORT: int = 1883
    MQTT_LISTEN_PORT_TLS: int = 8883
    XMPP_LISTEN_PORT: int = 1223
    XMPP_LISTEN_PORT_TLS: int = 5223

    # Servers
    mqtt_server: Optional["MQTTServer"] = None
    mqtt_helperbot: Optional["MQTTHelperBot"] = None
    web_server: Optional["WebServer"] = None
    xmpp_server: Optional["XMPPServer"] = None

    # Used for maintenance loop stop
    shutting_down: bool = False

    HOME_ID: str = "781a0733923f2240cf304757"


config: Config = Config()
