import json

import pytest

from bumper.utils import db
from bumper.web.auth_util import _generate_uid

USER_ID = _generate_uid("tmpuser")


@pytest.mark.usefixtures("clean_database")
async def test_getUsersAPI(webserver_client) -> None:
    resp = await webserver_client.post("/api/users/user.do", json={})
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "fail"


@pytest.mark.usefixtures("clean_database")
async def test_postUsersAPI(webserver_client) -> None:
    # Test FindBest
    postbody = {"todo": "FindBest", "service": "EcoMsgNew"}
    resp = await webserver_client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"

    # Test EcoUpdate
    postbody = {"todo": "FindBest", "service": "EcoUpdate"}
    resp = await webserver_client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"

    # Test loginByItToken - Uses the authcode
    db.user_add(USER_ID)
    db.user_add_device(USER_ID, "dev_1234")
    db.user_add_token(USER_ID, "token_1234")
    db.user_add_auth_code(USER_ID, "token_1234", "auth_1234")
    db.user_add_bot(USER_ID, "did_1234")
    db.bot_add("sn_1234", "did_1234", "class_1234", "res_1234", "com_1234")
    # Test
    postbody = {
        "country": "US",
        "last": "",
        "realm": "ecouser.net",
        "resource": "dev_1234",
        "todo": "loginByItToken",
        "token": "auth_1234",
        "userId": USER_ID,
    }
    resp = await webserver_client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"

    # Test as EcoVacs Home (global_e)
    postbody = {
        "country": "US",
        "edition": "ECOGLOBLE",
        "last": "",
        "org": "ECOWW",
        "resource": "dev_1234",
        "todo": "loginByItToken",
        "token": "auth_1234",
    }
    resp = await webserver_client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"

    # Test as EcoVacs Home (global_e) & Post Form
    postbody = {
        "country": "US",
        "edition": "ECOGLOBLE",
        "last": "",
        "org": "ECOWW",
        "resource": "dev_1234",
        "todo": "loginByItToken",
        "token": "auth_1234",
    }
    resp = await webserver_client.post("/api/users/user.do", data=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"

    # Test GetDeviceList
    postbody = {
        "auth": {
            "realm": "ecouser.net",
            "resource": "dev_1234",
            "token": "token_1234",
            "userid": USER_ID,
            "with": "users",
        },
        "todo": "GetDeviceList",
        "userid": USER_ID,
    }
    resp = await webserver_client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"

    # Test SetDeviceNick
    postbody = {
        "auth": {
            "realm": "ecouser.net",
            "resource": "dev_1234",
            "token": "token_1234",
            "userid": USER_ID,
            "with": "users",
        },
        "todo": "SetDeviceNick",
        "nick": "botnick",
        "did": "did_1234",
    }
    resp = await webserver_client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"

    # Test AddOneDevice - Same as set nick for some bots
    postbody = {
        "auth": {
            "realm": "ecouser.net",
            "resource": "dev_1234",
            "token": "token_1234",
            "userid": USER_ID,
            "with": "users",
        },
        "todo": "AddOneDevice",
        "nick": "botnick",
        "did": "did_1234",
    }
    resp = await webserver_client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"

    # Test DeleteOneDevice - remove bot
    postbody = {
        "auth": {
            "realm": "ecouser.net",
            "resource": "dev_1234",
            "token": "token_1234",
            "userid": USER_ID,
            "with": "users",
        },
        "todo": "DeleteOneDevice",
        "did": "did_1234",
    }
    resp = await webserver_client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"
