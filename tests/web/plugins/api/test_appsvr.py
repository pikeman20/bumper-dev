import json

import pytest

from bumper.utils import db
from bumper.web.auth_util import _generate_uid

USER_ID = _generate_uid("tmpuser")


@pytest.mark.usefixtures("clean_database", "mqtt_client")
async def test_appsvr_api(webserver_client):
    # Test GetGlobalDeviceList
    postbody = {
        "aliliving": False,
        "appVer": "1.1.6",
        "auth": {
            "realm": "ecouser.net",
            "resource": "ECOGLOBLEac5ae987",
            "token": "token_1234",
            "userid": USER_ID,
            "with": "users",
        },
        "channel": "google_play",
        "defaultLang": "en",
        "lang": "en",
        "platform": "Android",
        "todo": "GetGlobalDeviceList",
        "userid": USER_ID,
    }
    resp = await webserver_client.post("/api/appsvr/app.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["ret"] == "ok"

    db.bot_add("sn_1234", "did_1234", "ls1ok3", "res_1234", "eco-ng")

    # Test again with bot added
    resp = await webserver_client.post("/api/appsvr/app.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["ret"] == "ok"
