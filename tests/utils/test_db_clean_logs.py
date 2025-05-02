import pytest

from bumper.db import clean_log_repo
from bumper.web.models import CleanLog


@pytest.mark.usefixtures("clean_database")
def test_clean_logs_db() -> None:
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

    clean_log_repo.clear()
    assert len(clean_log_repo.list_by_did(did)) == 0

    clean_log_repo.add(did, cid, clean_log)
    assert len(clean_log_repo.list_by_did(did)) == 1

    rid = "sdu8"
    clean_log.clean_log_id = f"{did}@{start}@{rid}"
    clean_log_repo.add(did, cid, clean_log)
    assert len(clean_log_repo.list_by_did(did)) == 2

    clean_log.ts = 1699297517 + 1
    clean_log.clean_log_id = f"{did}@{clean_log.ts}@{rid}"
    clean_log_repo.add(did, cid, clean_log)
    assert len(clean_log_repo.list_by_did(did)) == 3

    rid = "sdu7"
    clean_log.clean_log_id = f"{did}@{start}@{rid}"
    clean_log_repo.add(did, cid, clean_log)
    assert len(clean_log_repo.list_by_did(did)) == 4

    did = "cßa9sbas"
    clean_log.clean_log_id = f"{did}@{clean_log.ts}@{rid}"
    clean_log_repo.add(did, cid, clean_log)
    assert len(clean_log_repo.list_by_did(did)) == 1

    clean_log.type = "area"
    clean_log_repo.add(did, cid, clean_log)
    assert len(clean_log_repo.list_by_did(did)) == 2

    clean_log_repo.clear()

    clean_log.type = "a"
    clean_log_repo.add(did, cid, clean_log)
    assert len(clean_log_repo.list_by_did(did)) == 1

    clean_log.type = "b"
    clean_log_repo.add(did, cid, clean_log)
    assert len(clean_log_repo.list_by_did(did)) == 2

    clean_log.type = "b"
    clean_log_repo.add(did, cid, clean_log)
    assert len(clean_log_repo.list_by_did(did)) == 2

    clean_log.last = 1699297520
    clean_log_repo.add(did, cid, clean_log)
    assert len(clean_log_repo.list_by_did(did)) == 2

    clean_log.area = 28
    clean_log_repo.add(did, cid, clean_log)
    assert len(clean_log_repo.list_by_did(did)) == 2
