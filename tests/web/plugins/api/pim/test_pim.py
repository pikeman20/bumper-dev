import json

import pytest


@pytest.mark.usefixtures("clean_database")
async def test_getProductIotMap(webserver_client) -> None:
    resp = await webserver_client.post("/api/pim/product/getProductIotMap")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == 0


async def test_pim_file(webserver_client) -> None:
    resp = await webserver_client.get("/api/pim/file/get/123")
    assert resp.status == 200
