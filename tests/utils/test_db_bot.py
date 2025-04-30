import pytest

from bumper.db import bot_repo


@pytest.mark.usefixtures("clean_database")
def test_bot_db() -> None:
    bot_repo.add("sn_123", "did_123", "dev_123", "res_123", "co_123")
    assert bot_repo.get("did_123")  # Test that bot was added to db

    bot_repo.set_nick("did_123", "nick_123")
    assert bot_repo.get("did_123").nick == "nick_123"  # Test that nick was added to bot

    bot_repo.set_mqtt("did_123", True)
    assert bot_repo.get("did_123").mqtt_connection  # Test that mqtt was set True for bot

    bot_repo.set_xmpp("did_123", True)
    assert bot_repo.get("did_123").xmpp_connection  # Test that xmpp was set True for bot

    bot_repo.reset_all_connections()
    assert bot_repo.get("did_123").mqtt_connection is False  # Test that mqtt was reset False for bot
    assert bot_repo.get("did_123").xmpp_connection is False  # Test that xmpp was reset False for bot

    bot_repo.remove("did_123")
    assert bot_repo.get("did_123") is None  # Test that bot is no longer in db
