from unittest.mock import MagicMock, patch

import pytest

import bumper
from bumper import utils
from bumper.utils.settings import config as bumper_isc
from tests import BUMPER_LISTEN


@pytest.mark.parametrize(
    ("cmd_args", "expected_level", "expected_verbose", "expected_listen", "expected_announce"),
    [
        (["--debug_level", "DEBUG"], "DEBUG", None, None, None),
        (["--debug_verbose", "3"], None, 3, None, None),
        (["--listen", "127.0.0.1"], None, None, "127.0.0.1", None),
        (["--announce", "127.0.0.1"], None, None, None, "127.0.0.1"),
        (["--debug_level", "DEBUG", "--listen", "127.0.0.1", "--announce", "127.0.0.1"], "DEBUG", None, "127.0.0.1", "127.0.0.1"),
    ],
)
@patch("bumper.start")
@patch("bumper.shutdown")
def test_argparse(
    mock_shutdown: MagicMock,
    mock_start: MagicMock,
    cmd_args: list[str],
    expected_level: str,
    expected_verbose: int,
    expected_listen: str,
    expected_announce: str,
):
    bumper_isc.ca_cert = "tests/_test_files/certs/ca.crt"
    bumper_isc.server_cert = "tests/_test_files/certs/bumper.crt"
    bumper_isc.server_key = "tests/_test_files/certs/bumper.key"

    bumper.main(cmd_args)

    if expected_level is not None:
        assert bumper_isc.bumper_level == expected_level
    if expected_verbose is not None:
        assert bumper_isc.bumper_verbose == expected_verbose
    if expected_listen is not None:
        assert bumper_isc.bumper_listen == expected_listen
    if expected_announce is not None:
        assert bumper_isc.bumper_announce_ip == expected_announce

    mock_start.assert_called()
    mock_shutdown.assert_called()


@patch("bumper.start")
@patch("bumper.shutdown")
def test_arg_listen_none(mock_shutdown: MagicMock, mock_start: MagicMock):
    bumper.main(["--listen", None])
    assert not utils.is_valid_ip(bumper_isc.bumper_listen)

    mock_start.assert_not_called()
    mock_shutdown.assert_called()

    # fallback, else other test reference on set none in this test ..
    bumper_isc.bumper_listen = BUMPER_LISTEN
