"""Provide helper functions for TinyDB operations."""

import logging
from typing import Any

from tinydb.table import Document

_LOGGER = logging.getLogger(__name__)


def warn_if_not_doc(obj: Any, name: str) -> None:
    """Warn if obj is not a Document and not None."""
    if not isinstance(obj, Document):
        _LOGGER.debug(f"'{name}' is not a TinyDB Document: '{type(obj)}'")
