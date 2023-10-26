from unittest.mock import patch

import bumper
from bumper.utils.settings import config as bumper_isc


def mock_subrun(*args):
    return args


@patch("bumper.start")
def test_argparse(mock_start):
    bumper_isc.ca_cert = "tests/test_certs/ca.crt"
    bumper_isc.server_cert = "tests/test_certs/bumper.crt"
    bumper_isc.server_key = "tests/test_certs/bumper.key"

    bumper.main(["--debug_level", "DEBUG"])
    assert bumper_isc.bumper_level == "DEBUG"
    assert mock_start.called is True

    bumper.main(["--debug_verbose", "3"])
    assert bumper_isc.bumper_verbose == 3
    assert mock_start.called is True

    bumper.main(["--listen", "127.0.0.1"])
    assert bumper_isc.bumper_listen == "127.0.0.1"
    assert mock_start.called is True

    bumper.main(["--announce", "127.0.0.1"])
    assert bumper_isc.bumper_announce_ip == "127.0.0.1"
    assert mock_start.called is True

    bumper.main(["--debug_level", "DEBUG", "--listen", "127.0.0.1", "--announce", "127.0.0.1"])
    assert bumper_isc.bumper_level == "DEBUG"
    assert bumper_isc.bumper_announce_ip == "127.0.0.1"
    assert bumper_isc.bumper_listen == "127.0.0.1"
    assert mock_start.called is True
