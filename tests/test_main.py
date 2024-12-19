import runpy
import sys
from unittest import mock

from testfixtures import LogCapture


# Patch the 'bumper' module's start and shutdown functions
@mock.patch("bumper.start")
@mock.patch("bumper.shutdown")
def test_main(mock_shutdown: mock.MagicMock, mock_start: mock.MagicMock) -> None:
    # Use LogCapture to verify logs
    with LogCapture():
        # Temporarily override sys.argv within a mock context
        with mock.patch.object(sys, "argv", []):
            # Run the module as if it were the main program
            runpy.run_module("bumper", run_name="__main__")

        # Assertions on the patched methods
        mock_start.assert_not_called()  # Ensure that 'start' was not called
        mock_shutdown.assert_called_once()  # Ensure that 'shutdown' was called once

        # If log capturing is needed, uncomment and assert as needed
        # log_capture.check_present("Shutting down...")
        # log_capture.check_present("Shutdown complete!")

        # Optionally check the logs if necessary
        # assert "Shutting down..." in log_capture.records
        # assert "Shutdown complete!" in log_capture.records
