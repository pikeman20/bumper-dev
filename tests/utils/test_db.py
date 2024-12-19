import os
from unittest import mock

import pytest
from tinydb.table import Document

from bumper.utils import db
from bumper.utils.settings import config as bumper_isc


def test_db_file_with_custom_env_var() -> None:
    custom_path = "/custom/path/to/database.db"
    with mock.patch.dict(os.environ, {"DB_FILE": custom_path}, clear=True):
        assert db._db_file() == custom_path


def test_db_file_with_empty_env_var() -> None:
    with mock.patch.dict(os.environ, {"DB_FILE": ""}, clear=True):
        assert db._db_file() == os.path.join(bumper_isc.data_dir, "bumper.db")


def test_db_file_with_none_env_var() -> None:
    env = os.environ.copy()
    env.pop("DB_FILE")
    with mock.patch.dict(os.environ, env, clear=True):
        assert db._db_file() == os.path.join(bumper_isc.data_dir, "bumper.db")


# def test_db_file_with_existing_custom_path():
#     custom_path = "/custom/path/to/database.db"
#     with mock.patch("os.path.exists", return_value=True), mock.patch("os.path.isfile", return_value=True):
#         assert db._db_file() == custom_path


# def test_db_file_with_nonexistent_custom_path():
#     custom_path = "/custom/nonexistent/path/database.db"
#     with mock.patch("os.path.exists", return_value=False):
#         assert db._db_file() == custom_path


# def test_db_file_with_default_data_dir():
#     with mock.patch("bumper.utils.settings.config.data_dir", "/default/data/dir"):
#         assert db._db_file() == os.path.join("/default/data/dir", "bumper.db")


@pytest.mark.asyncio
async def test_db_get(tmpdir) -> None:
    # Call the _db_get function
    with db._db_get() as result:
        # Verify that TinyDB was instantiated with the correct file path
        # assert result == db._db_file()

        result.drop_tables()

        result.table(db.TABLE_USERS).insert({})
        result.table(db.TABLE_CLIENTS).insert({})
        result.table(db.TABLE_BOTS).insert({})
        result.table(db.TABLE_TOKENS).insert({})
        result.table(db.TABLE_OAUTH).insert({})
        result.table(db.TABLE_CLEAN_LOGS).insert({})

        # Verify that tables were created
        assert db.TABLE_USERS in result.tables()
        assert db.TABLE_CLIENTS in result.tables()
        assert db.TABLE_BOTS in result.tables()
        assert db.TABLE_TOKENS in result.tables()
        assert db.TABLE_OAUTH in result.tables()
        assert db.TABLE_CLEAN_LOGS in result.tables()

        result.drop_tables()

        assert len(result) == 0


def test_logging_message_not_document() -> None:
    value_name = "test_value"

    # Case 1: None value
    value = None
    result = db._logging_message_not_document(value, value_name)
    assert result == f"'{value_name}' is not a 'Document' => <class 'NoneType'>"

    # Case 2: Single Document
    value = Document({"key": "value"}, 0)
    result = db._logging_message_not_document(value, value_name)
    assert result == f"'{value_name}' is not a 'Document' => <class 'tinydb.table.Document'>"

    # Case 3: List of Documents
    value = [Document({"key": "value"}, 0), Document({"key": "value"}, 0)]
    result = db._logging_message_not_document(value, value_name)
    assert result == f"'{value_name}' is not a 'Document' => <class 'list'>"

    # Case 4: Other types
    value = "some_string"
    result = db._logging_message_not_document(value, value_name)
    assert result == f"'{value_name}' is not a 'Document' => <class 'str'>"
