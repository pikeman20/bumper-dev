import pytest

from bumper.utils import db
from bumper.web.models import CleanLog


@pytest.mark.usefixtures("clean_database")
def test_clean_logs_db():
    did = "saocsa8c9basv"
    cid = "1699297517"
    start = 1699297517
    rid = "sdu9"
    clean_log = CleanLog(f"{did}@{start}@{rid}")
    clean_log.area = 28
    clean_log.last = 1699297517
    clean_log.stop_reason = 1
    clean_log.ts = start
    clean_log.type = "auto"

    db.clean_logs_clean()
    assert len(db.clean_log_by_id(did)) == 0

    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 1

    rid = "sdu8"
    clean_log.clean_log_id = f"{did}@{start}@{rid}"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 2

    cid = "cas0cbasv"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 3

    rid = "sdu7"
    clean_log.clean_log_id = f"{did}@{start}@{rid}"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 4

    did = "cßa9sbas"
    cid = "asicpasv98"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 1

    clean_log.type = "area"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 2

    db.clean_logs_clean()

    clean_log.type = "a"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 1

    clean_log.type = "b"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 2

    clean_log.type = "b"
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 2

    clean_log.last = 1699297520
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 2

    clean_log.area = 28
    db.clean_log_add(did, cid, clean_log)
    assert len(db.clean_log_by_id(did)) == 2

    db._update_clean_logs_list_field(did, cid, clean_log, False)
    assert len(db.clean_log_by_id(did)) == 1
