import json

import pytest

from bumper.web.models import RETURN_API_SUCCESS


@pytest.mark.usefixtures("clean_database")
async def test_checkVersion(webserver_client) -> None:
    resp = await webserver_client.get("/v1/private/us/en/dev_1234/ios/1/0/0/common/checkVersion")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS


@pytest.mark.usefixtures("clean_database")
async def test_checkAppVersion(webserver_client) -> None:
    resp = await webserver_client.get("/v1/private/us/en/dev_1234/global_e/1/0/0/common/checkAPPVersion")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS


@pytest.mark.usefixtures("clean_database")
async def test_uploadDeviceInfo(webserver_client) -> None:
    resp = await webserver_client.get("/v1/private/us/en/dev_1234/global_e/1/0/0/common/uploadDeviceInfo")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS


@pytest.mark.usefixtures("clean_database")
async def test_getSystemReminder(webserver_client) -> None:
    resp = await webserver_client.get("/v1/private/us/en/dev_1234/global_e/1/0/0/common/getSystemReminder")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS


async def test_getAreas(webserver_client) -> None:
    resp = await webserver_client.get("/v1/private/us/en/dev_1234/ios/1/0/0/common/getAreas")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
