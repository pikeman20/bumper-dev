import pytest

from bumper.utils import db


@pytest.mark.usefixtures("clean_database")
def test_oauth_db() -> None:
    db.user_add("testuser")  # Add testuser
    oauth = db.user_add_oauth("testuser")

    assert oauth is not None
    assert oauth.userId == "testuser"
    assert oauth.access_token is not None

    user_id1 = db.user_id_by_token(oauth.access_token)
    assert oauth.userId == user_id1

    db.user_revoke_expired_oauths("testuser")
    user_id2 = db.user_id_by_token(oauth.access_token)
    assert oauth.userId == user_id2

    db.revoke_expired_oauths()
    user_id2 = db.user_id_by_token(oauth.access_token)
    assert oauth.userId == user_id2
