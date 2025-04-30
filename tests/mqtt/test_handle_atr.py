import json
from typing import Any

import pytest

from bumper.db import clean_log_repo
from bumper.mqtt.handle_atr import clean_log


@pytest.mark.usefixtures("clean_database")
@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ("", 0),
        (None, 0),
        (1, 0),
        ("TEST", 0),
        ([], 0),
        ({}, 0),
        ({"body": {}}, 0),
        ({"body": {"data": {}}}, 0),
        ({"body": {"data": {"cid": "123"}}}, 0),
        ({"body": {"data": {"cid": "111", "start": "2023-01-01T00:00:00Z"}}}, 0),
        ({"body": {"data": {"cid": "123", "start": "2023-01-01T00:00:00Z"}}}, 1),
        (
            {
                "body": {
                    "data": {
                        "cid": "123",
                        "start": "2023-01-01T00:00:00Z",
                        "area": "living_room",
                        "time": "10",
                        "stopReason": "completed",
                        "type": "auto",
                    },
                },
            },
            1,
        ),
    ],
)
def test_clean_log(payload: dict[str, Any], expected: int) -> None:
    did = "test_device"
    rid = "test_rid"

    assert len(clean_log_repo.list_by_did(did)) == 0
    clean_log(did, rid, json.dumps(payload))
    assert len(clean_log_repo.list_by_did(did)) == expected

    if expected == 0:
        return
    start_p = payload.get("body", {}).get("data", {}).get("start")
    assert clean_log_repo.list_by_did(did)[0].clean_log_id == f"{did}@{start_p}@{rid}"
    assert clean_log_repo.list_by_did(did)[0].area == payload.get("body", {}).get("data", {}).get("area")
    assert clean_log_repo.list_by_did(did)[0].last == payload.get("body", {}).get("data", {}).get("time")
    assert clean_log_repo.list_by_did(did)[0].stop_reason == payload.get("body", {}).get("data", {}).get("stopReason")
    assert clean_log_repo.list_by_did(did)[0].ts == start_p
    assert clean_log_repo.list_by_did(did)[0].type == payload.get("body", {}).get("data", {}).get("type")
