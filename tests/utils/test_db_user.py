from datetime import datetime, timedelta

import pytest
from tinydb import TinyDB

from bumper.db import token_repo, user_repo
from bumper.db.db import QueryInstance
from bumper.utils.settings import config as bumper_isc
from bumper.web.models import BumperUser


@pytest.mark.usefixtures("clean_database")
def test_user_db() -> None:
    user_repo.add("new_testuser")
    assert user_repo.get_by_id("new_testuser").userid == "new_testuser"

    # Test user_add when user already exists
    user_repo.add("new_testuser")
    assert user_repo.get_by_id("new_testuser").userid == "new_testuser"  # User should still exist, not added again

    user_repo.add("testuser")  # Add testuser

    assert user_repo.get_by_id("testuser").userid == "testuser"  # Test that testuser was created and returned

    user_repo.add_device("testuser", "dev_1234")  # Add device to testuser

    assert user_repo.get_by_device_id("dev_1234").userid == "testuser"  # Test that testuser was found by deviceid

    user_repo.remove_device("testuser", "dev_1234")  # Remove device from testuser

    assert "dev_1234" not in user_repo.get_by_id("testuser").devices
    # Test that dev_1234 was not found in testuser devices

    user_repo.add_bot("testuser", "bot_1234")  # Add bot did to testuser

    assert "bot_1234" in user_repo.get_by_id("testuser").bots
    # Test that bot was found in testuser's bot list

    user_repo.remove_bot("testuser", "bot_1234")  # Remove bot did from testuser

    assert "bot_1234" not in user_repo.get_by_id("testuser").bots
    # Test that bot was not found in testuser's bot list

    token_repo.add("testuser", "token_1234")  # Add token to testuser

    assert token_repo.verify("testuser", "token_1234")
    # Test that token was found for testuser

    assert token_repo.get("testuser", "token_1234")
    assert token_repo.get_first("testuser")
    # Test that token was returned for testuser

    token_repo.add_auth_code("testuser", "auth_1234")  # Add authcode to token_1234 for testuser
    assert token_repo.verify_auth_code("testuser", "auth_1234")
    # Test that authcode was found for testuser

    token_repo.revoke_token("testuser", "token_1234")  # Remove authcode from testuser
    assert token_repo.verify_auth_code("testuser", "auth_1234") is False
    # Test that authcode was not found for testuser
    token_repo.revoke_token("testuser", "token_1234")  # Remove token from testuser
    assert token_repo.verify("testuser", "token_1234") is False  # Test that token was not found for testuser
    token_repo.add("testuser", "token_1234")  # Add token_1234
    token_repo.add("testuser", "token_4321")  # Add token_4321
    assert len(token_repo.list_for_user("testuser")) == 2  # Test 2 tokens are available
    assert token_repo.get_first("testuser")
    token_repo.revoke_all_for_user("testuser")  # Revoke all tokens
    assert len(token_repo.list_for_user("testuser")) == 0  # Test 0 tokens are available
    assert token_repo.get_first("testuser") is None

    # Test _user_full_upsert
    new_user = BumperUser(userid="new_testuser")
    user_repo._upsert(new_user.as_dict(), QueryInstance.userid == new_user.userid)
    assert user_repo.get_by_id("new_testuser").userid == "new_testuser"

    db_test = TinyDB("tests/_test_files/tmp.db")
    tokens = db_test.table("tokens")
    tokens.insert(
        {
            "userid": "testuser",
            "token": "token_123456",
            "expiration": f"{datetime.now(tz=bumper_isc.LOCAL_TIMEZONE) + timedelta(seconds=-10)}",
        },
    )  # Add expired token
    db_test.close()
    assert len(token_repo.list_for_user("testuser")) == 1  # Test 1 tokens are available
    assert token_repo.get_first("testuser")
    token_repo.revoke_user_expired("testuser")  # Revoke expired tokens
    assert len(token_repo.list_for_user("testuser")) == 0  # Test 0 tokens are available
    assert token_repo.get_first("testuser") is None

    db_test = TinyDB("tests/_test_files/tmp.db")
    tokens = db_test.table("tokens")
    tokens.insert(
        {
            "userid": "testuser",
            "token": "token_1234",
            "expiration": f"{datetime.now(tz=bumper_isc.LOCAL_TIMEZONE) + timedelta(seconds=-10)}",
        },
    )  # Add expired token
    db_test.close()
    assert len(token_repo.list_for_user("testuser")) == 1  # Test 1 tokens are available
    assert token_repo.get_first("testuser")
    token_repo.revoke_expired()  # Revoke expired tokens
    assert len(token_repo.list_for_user("testuser")) == 0  # Test 0 tokens are available
    assert token_repo.get_first("testuser") is None

    # Test login_by_it_token
    token_repo.add("testuser", "token_1234")
    token_repo.add_it_token("testuser", "auth_1234")
    login_result = token_repo.login_by_it_token("auth_1234")
    assert login_result.as_dict() == {"token": "token_1234", "userid": "testuser"}
