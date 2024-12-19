import json

import pytest

from bumper.web.models import RETURN_API_SUCCESS


@pytest.mark.usefixtures("clean_database")
async def test_homePageAlert(webserver_client) -> None:
    resp = await webserver_client.get("/v1/private/us/en/dev_1234/ios/1/0/0/campaign/homePageAlert")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == RETURN_API_SUCCESS
