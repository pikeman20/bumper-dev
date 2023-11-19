import asyncio
import json
from unittest import mock

import pytest

from bumper.mqtt.helper_bot import MQTTHelperBot
from bumper.utils import db
from bumper.web.auth_util import _generate_uid

USER_ID = _generate_uid("tmpuser")


def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


@pytest.mark.usefixtures("clean_database", "create_webserver")
async def test_lg_logs(webserver_client, helper_bot: MQTTHelperBot):
    db.bot_add("sn_1234", "did_1234", "ls1ok3", "res_1234", "eco-ng")
    db.bot_set_mqtt("did_1234", True)

    # Test return get status
    command_getstatus_resp = {
        "id": "resp_1234",
        "resp": "<ctl ret='ok' status='idle'/>",
        "ret": "ok",
    }
    helper_bot.send_command = mock.MagicMock(return_value=async_return(command_getstatus_resp))

    # Test GetGlobalDeviceList
    postbody = {
        "auth": {
            "realm": "ecouser.net",
            "resource": "ECOGLOBLEac5ae987",
            "token": "token_1234",
            "userid": USER_ID,
            "with": "users",
        },
        "did": "did_1234",
        "resource": "res_1234",
        "td": "GetCleanLogs",
    }
    resp = await webserver_client.post("/api/lg/log.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["ret"] == "ok"
