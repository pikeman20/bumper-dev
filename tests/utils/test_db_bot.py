import pytest

from bumper.utils import db


@pytest.mark.usefixtures("clean_database")
def test_bot_db():
    db.bot_add("sn_123", "did_123", "dev_123", "res_123", "co_123")
    assert db.bot_get("did_123")  # Test that bot was added to db

    db.bot_set_nick("did_123", "nick_123")
    assert db.bot_get("did_123").get("nick") == "nick_123"  # Test that nick was added to bot

    db.bot_set_mqtt("did_123", True)
    assert db.bot_get("did_123").get("mqtt_connection")  # Test that mqtt was set True for bot

    db.bot_set_xmpp("did_123", True)
    assert db.bot_get("did_123").get("xmpp_connection")  # Test that xmpp was set True for bot

    db.bot_reset_connection_status()
    assert db.bot_get("did_123").get("mqtt_connection") is False  # Test that mqtt was reset False for bot
    assert db.bot_get("did_123").get("xmpp_connection") is False  # Test that xmpp was reset False for bot

    db.bot_remove("did_123")
    assert db.bot_get("did_123") is None  # Test that bot is no longer in db
