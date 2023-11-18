from bumper.web.models import OAuth


def test_oauth():
    userId = "test"
    o_auth = OAuth.create_new(userId)
    assert o_auth is not None
    assert o_auth.userId == userId
    assert o_auth.access_token is not None
    assert o_auth.expire_at is not None
    assert o_auth.refresh_token is not None

    data = o_auth.to_response()
    assert data is not None
