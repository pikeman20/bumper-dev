import json

import pytest

from bumper.utils import db
from bumper.web.auth_util import _generate_uid
from bumper.web.models import ERR_TOKEN_INVALID, RETURN_API_SUCCESS

USER_ID = _generate_uid("tmpuser")


@pytest.mark.usefixtures("clean_database")
async def test_checkLogin(webserver_client) -> None:
    # Test without token
    resp = await webserver_client.get(f"/v1/private/us/en/dev_1234/ios/1/0/0/user/checkLogin?accessToken={None}")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert jsonresp["data"]["accessToken"] != "token_1234"
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]

    # Add a user to db and test with existing users
    db.user_add(USER_ID)
    resp = await webserver_client.get(f"/v1/private/us/en/dev_1234/ios/1/0/0/user/checkLogin?accessToken={None}")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert jsonresp["data"]["accessToken"] != "token_1234"
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]

    # Test again using global_e app
    db.user_add(USER_ID)
    resp = await webserver_client.get(f"/v1/private/us/en/dev_1234/global_e/1/0/0/user/checkLogin?accessToken={None}")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert jsonresp["data"]["accessToken"] != "token_1234"
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]

    # Remove dev from tmpuser
    db.user_remove_device(USER_ID, "dev_1234")

    # Add a token to user and test
    db.user_add(USER_ID)
    db.user_add_device(USER_ID, "dev_1234")
    db.user_add_token(USER_ID, "token_1234")
    resp = await webserver_client.get(f"/v1/private/us/en/dev_1234/ios/1/0/0/user/checkLogin?accessToken={'token_1234'}")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert jsonresp["data"]["accessToken"] == "token_1234"
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]

    # Test again using global_e app
    db.user_add(USER_ID)
    resp = await webserver_client.get(f"/v1/private/us/en/dev_1234/global_e/1/0/0/user/checkLogin?accessToken={'token_1234'}")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert jsonresp["data"]["accessToken"] == "token_1234"
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]


@pytest.mark.usefixtures("clean_database")
async def test_getAuthCode(webserver_client) -> None:
    # Test without user or token
    resp = await webserver_client.get(f"/v1/private/us/en/dev_1234/ios/1/0/0/user/getAuthCode?uid={None}&accessToken={None}")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == ERR_TOKEN_INVALID

    # # Test as global_e
    # resp = await webserver_client.get(f"/v1/global/auth/getAuthCode?uid={None}&deviceId=dev_1234")
    # assert resp.status == 200
    # text = await resp.text()
    # jsonresp = json.loads(text)
    # assert jsonresp["code"] == ERR_TOKEN_INVALID

    # Add a token to user and test
    db.user_add(USER_ID)
    db.user_add_device(USER_ID, "dev_1234")
    db.user_add_token(USER_ID, "token_1234")
    resp = await webserver_client.get("/v1/private/us/en/dev_1234/ios/1/0/0/user/getAuthCode?uid=testuser&accessToken=token_1234")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
    assert "authCode" in jsonresp["data"]
    assert "ecovacsUid" in jsonresp["data"]

    # The above should have added an authcode to token, try again to test with existing authcode
    resp = await webserver_client.get("/v1/private/us/en/dev_1234/ios/1/0/0/user/getAuthCode?uid=testuser&accessToken=token_1234")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
    assert "authCode" in jsonresp["data"]
    assert "ecovacsUid" in jsonresp["data"]


@pytest.mark.usefixtures("clean_database")
async def test_checkAgreement(webserver_client) -> None:
    resp = await webserver_client.get("/v1/private/us/en/dev_1234/ios/1/0/0/user/checkAgreement")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS

    # Test as global_e
    resp = await webserver_client.get("/v1/private/us/en/dev_1234/global_e/1/0/0/user/checkAgreement")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS


@pytest.mark.usefixtures("clean_database")
async def test_getUserAccountInfo(webserver_client) -> None:
    db.user_add(USER_ID)
    db.user_add_device(USER_ID, "dev_1234")
    db.user_add_token(USER_ID, "token_1234")
    db.user_add_auth_code(USER_ID, "token_1234", "auth_1234")
    db.user_add_bot(USER_ID, "did_1234")
    db.bot_add("sn_1234", "did_1234", "class_1234", "res_1234", "com_1234")

    resp = await webserver_client.get("/v1/private/us/en/dev_1234/global_e/1/0/0/user/getUserAccountInfo")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == "0000"
    assert jsonresp["msg"] == "The operation was successful"
    assert jsonresp["data"]["uid"] == USER_ID
