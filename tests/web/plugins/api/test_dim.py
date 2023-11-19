import asyncio
import json
from unittest import mock

import pytest

from bumper.mqtt.helper_bot import MQTTHelperBot
from bumper.utils import db


def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


@pytest.mark.usefixtures("clean_database", "create_webserver")
async def test_dim_devmanager(webserver_client, helper_bot: MQTTHelperBot):
    # Test PollSCResult
    postbody = {"td": "PollSCResult"}
    resp = await webserver_client.post("/api/dim/devmanager.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["ret"] == "ok"

    # Test HasUnreadMsg
    postbody = {"td": "HasUnreadMsg"}
    resp = await webserver_client.post("/api/dim/devmanager.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["ret"] == "ok"
    assert test_resp["unRead"] is False

    # Test BotCommand
    db.bot_add("sn_1234", "did_1234", "dev_1234", "res_1234", "eco-ng")
    db.bot_set_mqtt("did_1234", True)
    postbody = {"toId": "did_1234"}

    # Test return get status
    command_getstatus_resp = {
        "id": "resp_1234",
        "resp": "<ctl ret='ok' status='idle'/>",
        "ret": "ok",
    }
    helper_bot.send_command = mock.MagicMock(return_value=async_return(command_getstatus_resp))
    resp = await webserver_client.post("/api/dim/devmanager.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["ret"] == "ok"

    # Test return fail timeout
    command_timeout_resp = {"id": "resp_1234", "errno": "timeout", "ret": "fail"}
    helper_bot.send_command = mock.MagicMock(return_value=async_return(command_timeout_resp))
    resp = await webserver_client.post("/api/dim/devmanager.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["ret"] == "fail"
    assert test_resp["errno"] == "timeout"

    # Set bot not on mqtt
    db.bot_set_mqtt("did_1234", False)
    helper_bot.send_command = mock.MagicMock(return_value=async_return(command_getstatus_resp))
    resp = await webserver_client.post("/api/dim/devmanager.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["ret"] == "fail"
