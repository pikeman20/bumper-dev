import os
from datetime import datetime, timedelta
from unittest import mock

from tinydb import TinyDB

from bumper.utils import db
from bumper.utils.settings import config as bumper_isc
from bumper.web.models import CleanLog


def test_db_path():
    env = os.environ.copy()
    env.pop("DB_FILE")
    with mock.patch.dict(os.environ, env, clear=True):
        assert db._db_file() == os.path.join(bumper_isc.data_dir, "bumper.db")


def test_user_db():
    db.user_add("testuser")  # Add testuser

    assert db.user_by_user_id("testuser").userid == "testuser"  # Test that testuser was created and returned

    db.user_add_device("testuser", "dev_1234")  # Add device to testuser

    assert db.user_by_device_id("dev_1234").userid == "testuser"  # Test that testuser was found by deviceid

    db.user_remove_device("testuser", "dev_1234")  # Remove device from testuser

    assert "dev_1234" not in db.user_by_user_id("testuser").devices
    # Test that dev_1234 was not found in testuser devices

    db.user_add_bot("testuser", "bot_1234")  # Add bot did to testuser

    assert "bot_1234" in db.user_by_user_id("testuser").bots
    # Test that bot was found in testuser's bot list

    db.user_remove_bot("testuser", "bot_1234")  # Remove bot did from testuser

    assert "bot_1234" not in db.user_by_user_id("testuser").bots
    # Test that bot was not found in testuser's bot list

    db.user_add_token("testuser", "token_1234")  # Add token to testuser

    assert db.check_token("testuser", "token_1234")
    # Test that token was found for testuser

    assert db.user_get_token("testuser", "token_1234")
    # Test that token was returned for testuser

    db.user_add_auth_code("testuser", "token_1234", "auth_1234")  # Add authcode to token_1234 for testuser
    assert db.check_auth_code("testuser", "auth_1234")
    # Test that authcode was found for testuser

    db.user_revoke_auth_code("testuser", "token_1234")  # Remove authcode from testuser
    assert db.check_auth_code("testuser", "auth_1234") is False
    # Test that authcode was not found for testuser
    db.user_revoke_token("testuser", "token_1234")  # Remove token from testuser
    assert db.check_token("testuser", "token_1234") is False  # Test that token was not found for testuser
    db.user_add_token("testuser", "token_1234")  # Add token_1234
    db.user_add_token("testuser", "token_4321")  # Add token_4321
    assert len(db.user_get_tokens("testuser")) == 2  # Test 2 tokens are available
    db.user_revoke_all_tokens("testuser")  # Revoke all tokens
    assert len(db.user_get_tokens("testuser")) == 0  # Test 0 tokens are available

    db_test = TinyDB("tests/tmp.db")
    tokens = db_test.table("tokens")
    tokens.insert(
        {
            "userid": "testuser",
            "token": "token_123456",
            "expiration": f"{datetime.now() + timedelta(seconds=-10)}",
        }
    )  # Add expired token
    db_test.close()
    assert len(db.user_get_tokens("testuser")) == 1  # Test 1 tokens are available
    db.user_revoke_expired_tokens("testuser")  # Revoke expired tokens
    assert len(db.user_get_tokens("testuser")) == 0  # Test 0 tokens are available

    db_test = TinyDB("tests/tmp.db")
    tokens = db_test.table("tokens")
    tokens.insert(
        {
            "userid": "testuser",
            "token": "token_1234",
            "expiration": f"{datetime.now() + timedelta(seconds=-10)}",
        }
    )  # Add expired token
    db_test.close()
    assert len(db.user_get_tokens("testuser")) == 1  # Test 1 tokens are available
    db.revoke_expired_tokens()  # Revoke expired tokens
    assert len(db.user_get_tokens("testuser")) == 0  # Test 0 tokens are available


def test_bot_db():
    db.bot_add("sn_123", "did_123", "dev_123", "res_123", "co_123")
    assert db.bot_get("did_123")  # Test that bot was added to db

    db.bot_set_nick("did_123", "nick_123")
    assert db.bot_get("did_123").get("nick") == "nick_123"  # Test that nick was added to bot

    db.bot_set_mqtt("did_123", True)
    assert db.bot_get("did_123").get("mqtt_connection")  # Test that mqtt was set True for bot

    db.bot_set_xmpp("did_123", True)
    assert db.bot_get("did_123").get("xmpp_connection")  # Test that xmpp was set True for bot

    db.bot_remove("did_123")
    assert db.bot_get("did_123") is None  # Test that bot is no longer in db


def test_client_db():
    db.client_add("user_123", "realm_123", "resource_123")
    assert db.client_get("resource_123")  # Test client was added

    db.client_set_mqtt("resource_123", True)
    assert db.client_get("resource_123").get("mqtt_connection")  # Test that mqtt was set True for client

    db.client_set_xmpp("resource_123", False)
    assert db.client_get("resource_123").get("xmpp_connection") is False  # Test that xmpp was set False for client
    assert len(db.get_disconnected_xmpp_clients()) > 0  # Test len of connected xmpp clients is 1

    db.client_remove("resource_123")
    assert db.client_get("resource_123") is None


def test_clean_logs_db():
    did = "saocsa8c9basv"
    cid = "1699297517"
    start = 1699297517
    rid = "sdu9"
    clean_log = CleanLog(f"{did}@{start}@{rid}")
    clean_log.area = 28
    clean_log.last = 1699297517
    clean_log.stop_reason = 1
    clean_log.ts = start
    clean_log.type = "auto"

    db.clean_logs_clean()

    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 1

    rid = "sdu8"
    clean_log.clean_log_id = f"{did}@{start}@{rid}"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 2

    cid = "cas0cbasv"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 3

    rid = "sdu7"
    clean_log.clean_log_id = f"{did}@{start}@{rid}"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 4

    did = "cßa9sbas"
    cid = "asicpasv98"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 1

    clean_log.type = "area"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 2

    db.clean_logs_clean()

    clean_log.type = "a"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 1

    clean_log.type = "b"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 2

    clean_log.type = "b"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 2

    clean_log.last = 1699297520
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 2

    clean_log.area = 28
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 2
