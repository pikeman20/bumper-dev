"""Manage clean log entries."""

import logging
from typing import Any

from tinydb.table import Document

from bumper.web import models

from .base import BaseRepo
from .db import TABLE_CLEAN_LOGS, QueryInstance
from .helpers import warn_if_not_doc

_LOGGER = logging.getLogger(__name__)


class CleanLogRepo(BaseRepo):
    """DAO for clean logs."""

    def __init__(self) -> None:
        super().__init__(TABLE_CLEAN_LOGS)

    def add(self, did: str, cid: str, log: models.CleanLog) -> None:
        """Add or update a clean log entry."""
        q = (QueryInstance.did == did) & (QueryInstance.cid == cid)
        entry = self._get(q)
        if not isinstance(entry, dict | Document):
            self._upsert(models.CleanLogs(did, cid).to_db(), q)
            entry = self._get(q)
        if not isinstance(entry, dict | Document):
            warn_if_not_doc(entry, "CleanLogRepo.add entry")
            return
        logs: list[dict[str, Any]] = list(entry.get("logs", []))
        updated = False
        for idx, raw in enumerate(logs):
            existing = models.CleanLog.from_dict(raw)
            if existing.clean_log_id == log.clean_log_id and existing.ts == log.ts and existing.type == log.type:
                logs[idx] = log.to_db()
                updated = True
                break
        if not updated:
            logs.append(log.to_db())
        self._upsert({"logs": logs}, q)

    def list_by_did(self, did: str) -> list[models.CleanLog]:
        """List clean logs by device ID."""
        results: list[models.CleanLog] = []
        for entry in self.table.search(QueryInstance.did == did):
            warn_if_not_doc(entry, "CleanLogRepo.list_by_did entry")
            results.extend(models.CleanLog.from_dict(raw) for raw in entry.get("logs", []))
        return results

    def clear(self) -> None:
        """Clear all clean logs."""
        self.table.truncate()
