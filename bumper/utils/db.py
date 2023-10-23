"""Database module."""
import logging
import os
from datetime import datetime, timedelta
from typing import Any

from tinydb import Query, TinyDB
from tinydb.table import Document

from bumper.utils.settings import config as bumper_isc
from bumper.web import models

_LOGGER = logging.getLogger("db")


def logging_message_none_or_not_document(value: Document | list[Document] | None, value_name: str) -> str:
    """Log Helper for generic not a Document info."""
    return f"'{value_name}' is not a 'Document' => {type(value)}"


def _db_file() -> str:
    return os.environ.get("DB_FILE") or _os_db_path()


def _os_db_path() -> str:  # createdir=True):
    return os.path.join(bumper_isc.data_dir, "bumper.db")


TABLE_USERS = "users"
TABLE_CLIENTS = "clients"
TABLE_BOTS = "bots"
TABLE_TOKENS = "tokens"
TABLE_OAUTH = "oath"


def _db_get() -> TinyDB:
    # Will create the database if it doesn't exist
    db = TinyDB(_db_file())

    # Will create the tables if they don't exist
    db.table(TABLE_USERS, cache_size=0)
    db.table(TABLE_CLIENTS, cache_size=0)
    db.table(TABLE_BOTS, cache_size=0)
    db.table(TABLE_TOKENS, cache_size=0)
    db.table(TABLE_OAUTH, cache_size=0)

    return db


def user_add(userid: str) -> None:
    """Add user."""
    newuser = models.BumperUser()
    newuser.userid = userid

    user = user_get(userid)
    if user is None:
        _LOGGER.info(f"Adding new user with userid: {newuser.userid}")
        _user_full_upsert(newuser.asdict())


def user_get(userid: str) -> Document | None:
    """Get user."""
    users = _db_get().table(TABLE_USERS)
    t_user = users.get(Query().userid == userid)
    if isinstance(t_user, Document):
        return t_user
    if t_user is not None:
        _LOGGER.warning(logging_message_none_or_not_document(t_user, "t_user"))
    return None


def user_by_device_id(deviceid: str) -> Document | None:
    """Get user by device id."""
    users = _db_get().table(TABLE_USERS)
    t_user = users.get(Query().devices.any([deviceid]))
    if isinstance(t_user, Document):
        return t_user
    if t_user is not None:
        _LOGGER.warning(logging_message_none_or_not_document(t_user, "t_user"))
    return None


def _user_full_upsert(user: dict[str, Any]) -> None:
    opendb = _db_get()
    with opendb:
        users = opendb.table(TABLE_USERS)
        users.upsert(user, Query().did == user["userid"])


def user_add_device(userid: str, devid: str) -> None:
    """Add device to user."""
    opendb = _db_get()
    with opendb:
        users = opendb.table(TABLE_USERS)
        t_user = users.get(Query().userid == userid)
        if isinstance(t_user, Document):
            userdevices = list(t_user["devices"])
            if devid not in userdevices:
                userdevices.append(devid)
            users.upsert({"devices": userdevices}, Query().userid == userid)
        elif t_user is not None:
            _LOGGER.warning(logging_message_none_or_not_document(t_user, "t_user"))


def user_remove_device(userid: str, devid: str) -> None:
    """Remove device from user."""
    opendb = _db_get()
    with opendb:
        users = opendb.table(TABLE_USERS)
        t_user = users.get(Query().userid == userid)
        if isinstance(t_user, Document):
            userdevices = list(t_user["devices"])
            if devid in userdevices:
                userdevices.remove(devid)
            users.upsert({"devices": userdevices}, Query().userid == userid)
        elif t_user is not None:
            _LOGGER.warning(logging_message_none_or_not_document(t_user, "t_user"))


def user_add_bot(userid: str, did: str) -> None:
    """Add bot to user."""
    opendb = _db_get()
    with opendb:
        users = opendb.table(TABLE_USERS)
        t_user = users.get(Query().userid == userid)
        if isinstance(t_user, Document):
            userbots = list(t_user[TABLE_BOTS])
            if did not in userbots:
                userbots.append(did)
            users.upsert({TABLE_BOTS: userbots}, Query().userid == userid)
        elif t_user is not None:
            _LOGGER.warning(logging_message_none_or_not_document(t_user, "t_user"))


def user_remove_bot(userid: str, did: str) -> None:
    """Remove bot from user."""
    opendb = _db_get()
    with opendb:
        users = opendb.table(TABLE_USERS)
        t_user = users.get(Query().userid == userid)
        if isinstance(t_user, Document):
            userbots = list(t_user[TABLE_BOTS])
            if did in userbots:
                userbots.remove(did)
            users.upsert({TABLE_BOTS: userbots}, Query().userid == userid)
        elif t_user is not None:
            _LOGGER.warning(logging_message_none_or_not_document(t_user, "t_user"))


def user_get_tokens(userid: str) -> list[Document]:
    """Get all tokens by given user."""
    tokens = _db_get().table(TABLE_TOKENS)
    return tokens.search(Query().userid == userid)


def user_get_token(userid: str, token: str) -> Document | None:
    """Get token by user."""
    tokens = _db_get().table(TABLE_TOKENS)
    t_token = tokens.get((Query().userid == userid) & (Query().token == token))
    if isinstance(t_token, Document):
        return t_token
    if t_token is not None:
        _LOGGER.warning(logging_message_none_or_not_document(t_token, "t_token"))
    return None


def user_add_token(userid: str, token: str) -> None:
    """Ass token for given user."""
    opendb = _db_get()
    with opendb:
        tokens = opendb.table(TABLE_TOKENS)
        t_token = tokens.get((Query().userid == userid) & (Query().token == token))
        if not t_token:
            _LOGGER.debug(f"Adding token {token} for userid {userid}")
            tokens.insert(
                {
                    "userid": userid,
                    "token": token,
                    "expiration": str(datetime.now() + timedelta(seconds=bumper_isc.TOKEN_VALIDITY_SECONDS)),
                }
            )


def user_revoke_all_tokens(userid: str) -> None:
    """Revoke all tokens for given user."""
    opendb = _db_get()
    with opendb:
        tokens = opendb.table(TABLE_TOKENS)
        tsearch = tokens.search(Query().userid == userid)
        for i in tsearch:
            tokens.remove(doc_ids=[i.doc_id])


def user_revoke_expired_tokens(userid: str) -> None:
    """Revoke expired user tokens."""
    opendb = _db_get()
    with opendb:
        tokens = opendb.table(TABLE_TOKENS)
        tsearch = tokens.search(Query().userid == userid)
        for i in tsearch:
            if datetime.now() >= datetime.fromisoformat(i["expiration"]):
                _LOGGER.debug(f"Removing token {i['token']} due to expiration")
                tokens.remove(doc_ids=[i.doc_id])


def user_revoke_token(userid: str, token: str) -> None:
    """Revoke user token."""
    opendb = _db_get()
    with opendb:
        tokens = opendb.table(TABLE_TOKENS)
        t_token = tokens.get((Query().userid == userid) & (Query().token == token))
        if isinstance(t_token, Document):
            tokens.remove(doc_ids=[t_token.doc_id])
        elif t_token is not None:
            _LOGGER.warning(logging_message_none_or_not_document(t_token, "t_token"))


def user_add_authcode(userid: str, token: str, authcode: str) -> None:
    """Add user authcode."""
    opendb = _db_get()
    with opendb:
        tokens = opendb.table(TABLE_TOKENS)
        t_token = tokens.get((Query().userid == userid) & (Query().token == token))
        if t_token:
            tokens.upsert(
                {"authcode": authcode},
                ((Query().userid == userid) & (Query().token == token)),
            )


def user_revoke_authcode(userid: str, token: str) -> None:
    """Revoke user authcode."""
    opendb = _db_get()
    with opendb:
        tokens = opendb.table(TABLE_TOKENS)
        t_token = tokens.get((Query().userid == userid) & (Query().token == token))
        if t_token:
            tokens.upsert(
                {"authcode": ""},
                ((Query().userid == userid) & (Query().token == token)),
            )


def revoke_expired_oauths() -> None:
    """Revoke expired oauths."""
    opendb = _db_get()
    with opendb:
        table = opendb.table(TABLE_OAUTH)
        entries = table.all()

        for i in entries:
            oauth = models.OAuth(**i)
            if datetime.now() >= datetime.fromisoformat(oauth.expire_at):
                _LOGGER.debug(f"Removing oauth {oauth.access_token} due to expiration")
                table.remove(doc_ids=[i.doc_id])


def user_revoke_expired_oauths(userid: str) -> None:
    """Revoke expired oauths by user."""
    opendb = _db_get()
    with opendb:
        table = opendb.table(TABLE_OAUTH)
        search = table.search(Query().userid == userid)
        for i in search:
            oauth = models.OAuth(**i)
            if datetime.now() >= datetime.fromisoformat(oauth.expire_at):
                _LOGGER.debug(f"Removing oauth {oauth.access_token} due to expiration")
                table.remove(doc_ids=[i.doc_id])


def user_add_oauth(userid: str) -> models.OAuth | None:
    """Add oauth for user."""
    user_revoke_expired_oauths(userid)
    opendb = _db_get()
    with opendb:
        table = opendb.table(TABLE_OAUTH)
        entry = table.get(Query().userid == userid)
        if isinstance(entry, Document):
            return models.OAuth(**entry)
        if entry is None:
            oauth = models.OAuth.create_new(userid)
            _LOGGER.debug(f"Adding oauth {oauth.access_token} for userid {userid}")
            table.insert(oauth.to_db())
            return oauth
        _LOGGER.warning(logging_message_none_or_not_document(entry, "entry"))
    return None


def token_by_authcode(authcode: str) -> Document | None:
    """Get token by authcode."""
    tokens = _db_get().table(TABLE_TOKENS)
    t_token = tokens.get(Query().authcode == authcode)
    if isinstance(t_token, Document):
        return t_token
    if t_token is not None:
        _LOGGER.warning(logging_message_none_or_not_document(t_token, "t_token"))
    return None


def get_disconnected_xmpp_clients() -> list[Document]:
    """Get disconnected XMPP clients."""
    clients = _db_get().table(TABLE_CLIENTS)
    return clients.search(Query().xmpp_connection == False)  # noqa: E712


def check_authcode(uid: str, authcode: str) -> bool:
    """Check authcode."""
    _LOGGER.debug(f"Checking for authcode: {authcode}")
    tokens = _db_get().table(TABLE_TOKENS)
    tmpauth = tokens.get(
        (Query().authcode == authcode)
        & (  # Match authcode
            (Query().userid == uid.replace("fuid_", "")) | (Query().userid == f"fuid_{uid}")
        )  # Userid with or without fuid_
    )
    if tmpauth is not None:
        return True
    return False


def login_by_it_token(authcode: str) -> dict[str, str]:
    """Login by token."""
    _LOGGER.debug(f"Checking for authcode: {authcode}")
    tokens = _db_get().table(TABLE_TOKENS)
    t_auth = tokens.get(
        Query().authcode
        == authcode
        # & (  # Match authcode
        #    (Query().userid == uid.replace("fuid_", ""))
        #    | (Query().userid == "fuid_{}".format(uid))
        # )  # Userid with or without fuid_
    )
    if isinstance(t_auth, Document):
        return {"token": t_auth["token"], "userid": t_auth["userid"]}
    if t_auth is not None:
        _LOGGER.warning(logging_message_none_or_not_document(t_auth, "t_auth"))
    return {}


def check_token(uid: str, token: str) -> bool:
    """Check token."""
    _LOGGER.debug(f"Checking for token: {token}")
    tokens = _db_get().table(TABLE_TOKENS)
    t_auth = tokens.get(
        (Query().token == token)
        & (  # Match token
            (Query().userid == uid.replace("fuid_", "")) | (Query().userid == f"fuid_{uid}")
        )  # Userid with or without fuid_
    )
    if t_auth is not None:
        return True
    return False


def revoke_expired_tokens() -> None:
    """Revoke expired tokens."""
    tokens = _db_get().table(TABLE_TOKENS).all()
    for i in tokens:
        if datetime.now() >= datetime.fromisoformat(i["expiration"]):
            _LOGGER.debug(f"Removing token {i['token']} due to expiration")
            _db_get().table(TABLE_TOKENS).remove(doc_ids=[i.doc_id])


def bot_add(sn: str, did: str, dev_class: str, resource: str, company: str) -> None:
    """Add bot."""
    new_bot = models.VacBotDevice()
    new_bot.did = did
    new_bot.name = sn
    new_bot.vac_bot_device_class = dev_class
    new_bot.resource = resource
    new_bot.company = company

    bot = bot_get(did)
    # Not existing bot in database
    # AND try to prevent bad additions to the bot list
    if bot is None and (not dev_class == "" or "@" not in sn or "tmp" not in sn):
        _LOGGER.info(f"Adding new bot with SN: {new_bot.name} DID: {new_bot.did}")
        bot_full_upsert(new_bot.asdict())


def bot_get_all() -> list[Document]:
    """Get all bots."""
    return _db_get().table(TABLE_BOTS).all()


def bot_remove(did: str) -> None:
    """Remove bot."""
    bots = _db_get().table(TABLE_BOTS)
    t_bot = bot_get(did)
    if t_bot is not None:
        bots.remove(doc_ids=[t_bot.doc_id])


def bot_get(did: str) -> Document | None:
    """Get bot."""
    bots = _db_get().table(TABLE_BOTS)
    t_bot = bots.get(Query().did == did)
    if isinstance(t_bot, Document):
        return t_bot
    if t_bot is not None:
        _LOGGER.warning(logging_message_none_or_not_document(t_bot, "t_bot"))
    return None


def bot_full_upsert(vacbot: dict[str, Any]) -> None:
    """Upsert bot."""
    bots = _db_get().table(TABLE_BOTS)
    if "did" in vacbot:
        bots.upsert(vacbot, Query().did == vacbot["did"])
    else:
        _LOGGER.error(f"No DID in vacbot :: {vacbot}")


def bot_set_nick(did: str, nick: str) -> None:
    """Bot set nickname."""
    bots = _db_get().table(TABLE_BOTS)
    bots.upsert({"nick": nick}, Query().did == did)


def bot_set_mqtt(did: str, mqtt: bool) -> None:
    """Bot ste MQTT status."""
    bots = _db_get().table(TABLE_BOTS)
    bots.upsert({"mqtt_connection": mqtt}, Query().did == did)


def bot_set_xmpp(did: str, xmpp: bool) -> None:
    """Bot set XMPP status."""
    bots = _db_get().table(TABLE_BOTS)
    bots.upsert({"xmpp_connection": xmpp}, Query().did == did)


def client_get_all() -> list[Document]:
    """Get all bots."""
    return _db_get().table(TABLE_CLIENTS).all()


def client_add(userid: str, realm: str, resource: str) -> None:
    """Add client."""
    new_client = models.VacBotClient()
    new_client.userid = userid
    new_client.realm = realm
    new_client.resource = resource

    client = client_get(resource)
    if client is None:
        _LOGGER.info(f"Adding new client with resource {new_client.resource}")
        _client_full_upsert(new_client.asdict())


def client_remove(resource: str) -> None:
    """Remove client."""
    clients = _db_get().table(TABLE_CLIENTS)
    t_client = client_get(resource)
    if t_client is not None:
        clients.remove(doc_ids=[t_client.doc_id])


def client_get(resource: str) -> Document | None:
    """Get client by resource."""
    clients = _db_get().table(TABLE_CLIENTS)
    t_client = clients.get(Query().resource == resource)
    if isinstance(t_client, Document):
        return t_client
    if t_client is not None:
        _LOGGER.warning(logging_message_none_or_not_document(t_client, "t_client"))
    return None


def _client_full_upsert(client: dict[str, Any]) -> None:
    clients = _db_get().table(TABLE_CLIENTS)
    clients.upsert(client, Query().resource == client["resource"])


def client_set_mqtt(resource: str, mqtt: bool) -> None:
    """Client set MQTT status."""
    clients = _db_get().table(TABLE_CLIENTS)
    clients.upsert({"mqtt_connection": mqtt}, Query().resource == resource)


def client_set_xmpp(resource: str, xmpp: bool) -> None:
    """Client set XMPP status."""
    clients = _db_get().table(TABLE_CLIENTS)
    clients.upsert({"xmpp_connection": xmpp}, Query().resource == resource)


def bot_reset_connection_status() -> None:
    """Reset all bot connection status."""
    bots = _db_get().table(TABLE_BOTS)
    for bot in bots:
        bot_set_mqtt(bot["did"], False)
        bot_set_xmpp(bot["did"], False)


def client_reset_connection_status() -> None:
    """Reset all client connection status."""
    clients = _db_get().table(TABLE_CLIENTS)
    for client in clients:
        client_set_mqtt(client["resource"], False)
        client_set_xmpp(client["resource"], False)
