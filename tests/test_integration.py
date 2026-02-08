"""Integration tests for exception reporting."""

import os
import sys
import tempfile
import threading
import time
from unittest.mock import patch

from reportit import Reporter, disable, enable
from reportit.hooks import is_hooks_installed


class TestIntegration:
    """Integration tests for full exception flow."""

    def test_file_bridge_integration(self):
        """Test full integration with file bridge."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "exceptions.log")

            # Enable reporting
            enable(bridge="file", log_file=log_file, enabled=True)

            try:
                # Raise an exception
                raise ValueError("integration test error")
            except ValueError:
                # Exception should be caught and reported
                pass

            # Give time for async operations (if any)
            time.sleep(0.1)

            # Verify exception was logged
            assert os.path.exists(log_file)
            with open(log_file) as f:
                content = f.read()
                assert "integration test error" in content
                assert "ValueError" in content

            # Cleanup
            disable()

    def test_thread_exception_integration(self):
        """Test integration with thread exceptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "exceptions.log")

            # Enable reporting
            enable(bridge="file", log_file=log_file, enabled=True)

            exception_raised = threading.Event()

            def worker():
                try:
                    raise RuntimeError("thread exception")
                except RuntimeError:
                    exception_raised.set()
                    raise

            thread = threading.Thread(target=worker)
            thread.start()
            thread.join()

            # Give time for reporting
            time.sleep(0.1)

            # Verify exception was logged
            assert os.path.exists(log_file)
            with open(log_file) as f:
                content = f.read()
                assert "thread exception" in content
                assert "RuntimeError" in content

            # Cleanup
            disable()

    def test_uncaught_exception_integration(self):
        """Test integration with uncaught exceptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "exceptions.log")

            # Enable reporting
            enable(bridge="file", log_file=log_file, enabled=True)

            # Create a function that raises an uncaught exception
            def raise_uncaught():
                raise KeyError("uncaught exception")

            # Run in a subprocess-like way
            # We'll use a thread to simulate this
            def run_with_exception():
                try:
                    raise_uncaught()
                except KeyError as e:
                    # Simulate uncaught by calling excepthook directly
                    sys.excepthook(type(e), e, e.__traceback__)

            thread = threading.Thread(target=run_with_exception)
            thread.start()
            thread.join()

            # Give time for reporting
            time.sleep(0.1)

            # Verify exception was logged
            assert os.path.exists(log_file)
            with open(log_file) as f:
                content = f.read()
                assert "uncaught exception" in content
                assert "KeyError" in content

            # Cleanup
            disable()

    def test_multiple_exceptions_integration(self):
        """Test integration with multiple exceptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "exceptions.log")

            # Enable reporting
            enable(bridge="file", log_file=log_file, enabled=True)

            # Raise multiple exceptions
            for i in range(3):
                try:
                    raise ValueError(f"exception {i}")
                except ValueError:
                    pass

            # Give time for reporting
            time.sleep(0.1)

            # Verify all exceptions were logged
            assert os.path.exists(log_file)
            with open(log_file) as f:
                content = f.read()
                assert content.count("Exception Report") == 3
                assert "exception 0" in content
                assert "exception 1" in content
                assert "exception 2" in content

            # Cleanup
            disable()

    def test_disable_stops_reporting(self):
        """Test that disabling stops exception reporting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "exceptions.log")

            # Enable reporting
            enable(bridge="file", log_file=log_file, enabled=True)

            # Raise an exception
            try:
                raise ValueError("before disable")
            except ValueError:
                pass

            time.sleep(0.1)

            # Disable reporting
            disable()

            # Raise another exception
            try:
                raise ValueError("after disable")
            except ValueError:
                pass

            time.sleep(0.1)

            # Verify only first exception was logged
            assert os.path.exists(log_file)
            with open(log_file) as f:
                content = f.read()
                assert "before disable" in content
                assert "after disable" not in content

    def test_reporter_class_integration(self):
        """Test integration using Reporter class directly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "exceptions.log")

            from reportit.bridges import create_bridges

            bridges = create_bridges("file", log_file=log_file)
            from reportit.config import Config

            config = Config(enabled=True)
            reporter = Reporter(bridges=bridges, config=config)
            reporter.enable()

            # Report an exception manually
            try:
                raise ValueError("manual report")
            except ValueError as e:
                reporter.report_exception(type(e), e, e.__traceback__)

            time.sleep(0.1)

            # Verify exception was logged
            assert os.path.exists(log_file)
            with open(log_file) as f:
                content = f.read()
                assert "manual report" in content

            reporter.disable()

    def test_environment_variable_integration(self):
        """Test integration with environment variable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "exceptions.log")

            with patch.dict(os.environ, {"CURSOR_EXCEPTION_REPORTING": "true"}):
                # Enable without explicit enabled parameter
                enable(bridge="file", log_file=log_file)

                try:
                    raise ValueError("env var test")
                except ValueError:
                    pass

                time.sleep(0.1)

                # Verify exception was logged
                assert os.path.exists(log_file)
                with open(log_file) as f:
                    content = f.read()
                    assert "env var test" in content

                disable()

    def test_hooks_installation_state(self):
        """Test that hooks installation state is tracked correctly."""
        assert not is_hooks_installed()

        enable(enabled=True, bridge="file")
        assert is_hooks_installed()

        disable()
        assert not is_hooks_installed()
