import runpy
import sys
from unittest.mock import MagicMock, patch

from testfixtures import LogCapture


@patch("bumper.start")
@patch("bumper.shutdown")
def test_main(
    mock_shutdown: MagicMock,
    mock_start: MagicMock,
):
    with LogCapture() as _:
        original_argv = sys.argv  # Save the original sys.argv
        sys.argv = []  # Set the expected command-line arguments

        runpy.run_module("bumper", run_name="__main__")

        # log.check_present("Shutting down...")
        # log.check_present("Shutdown complete!")

        mock_start.assert_not_called()
        mock_shutdown.assert_called_once()

        sys.argv = original_argv  # Restore the original sys.argv
