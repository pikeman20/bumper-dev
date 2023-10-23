from unittest.mock import patch

import bumper
from bumper.utils.settings import config as bumper_bus


def mock_subrun(*args):
    return args


@patch("bumper.start")
def test_argparse(mock_start):
    bumper_bus.ca_cert = "tests/test_certs/ca.crt"
    bumper_bus.server_cert = "tests/test_certs/bumper.crt"
    bumper_bus.server_key = "tests/test_certs/bumper.key"

    bumper.main(["--debug"])
    assert bumper_bus.bumper_level == "DEBUG"
    assert mock_start.called == True

    bumper.main(["--listen", "127.0.0.1"])
    assert bumper_bus.bumper_listen == "127.0.0.1"
    assert mock_start.called == True

    bumper.main(["--announce", "127.0.0.1"])
    assert bumper_bus.bumper_announce_ip == "127.0.0.1"
    assert mock_start.called == True

    bumper.main(["--debug", "--listen", "127.0.0.1", "--announce", "127.0.0.1"])
    assert bumper_bus.bumper_level == "DEBUG"
    assert bumper_bus.bumper_announce_ip == "127.0.0.1"
    assert bumper_bus.bumper_listen == "127.0.0.1"
    assert mock_start.called == True
