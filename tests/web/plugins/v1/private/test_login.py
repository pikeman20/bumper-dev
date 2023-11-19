import json

import pytest

from bumper.utils import db
from bumper.web.auth_util import _generate_uid
from bumper.web.models import RETURN_API_SUCCESS, VacBotDevice

USER_ID = _generate_uid("tmpuser")


@pytest.mark.usefixtures("clean_database")
async def test_login_with_user(webserver_client):
    # Test without user
    resp = await webserver_client.get("/v1/private/us/en/dev_1234/ios/1/0/0/user/login")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]


@pytest.mark.usefixtures("clean_database")
async def test_login_without_user(webserver_client):
    # Test global_e without user
    resp = await webserver_client.get("/v1/private/us/en/dev_1234/global_e/1/0/0/user/login")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]


@pytest.mark.usefixtures("clean_database")
async def test_login_with_existing_user(webserver_client):
    # Add a user to db and test with existing users
    db.user_add(USER_ID)
    resp = await webserver_client.get("/v1/private/us/en/dev_1234/ios/1/0/0/user/login")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]

    # Add a bot to db that will be added to user
    db.bot_add("sn_123", "did_123", "dev_123", "res_123", "com_123")
    resp = await webserver_client.get("/v1/private/us/en/dev_1234/ios/1/0/0/user/login")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]

    # Add a bot to db that doesn't have a did
    newbot = {
        "class": "dev_1234",
        "company": "com_123",
        # "did": self.did,
        "name": "sn_1234",
        "resource": "res_1234",
    }
    db.bot_full_upsert(VacBotDevice.from_dict(newbot))

    resp = await webserver_client.get("/v1/private/us/en/dev_1234/ios/1/0/0/user/login")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]


@pytest.mark.usefixtures("clean_database")
async def test_logout(webserver_client):
    # Add a token to user and test
    db.user_add(USER_ID)
    db.user_add_device(USER_ID, "dev_1234")
    db.user_add_token(USER_ID, "token_1234")
    resp = await webserver_client.get(f"/v1/private/us/en/dev_1234/ios/1/0/0/user/logout?accessToken={'token_1234'}")

    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
