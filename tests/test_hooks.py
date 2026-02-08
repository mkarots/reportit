"""Tests for hooks module."""

import sys
import threading
from unittest.mock import Mock, patch

import pytest

from reportit.hooks import (
    install_hooks,
    uninstall_hooks,
    is_hooks_installed,
)
from reportit.reporter import Reporter


class TestHooks:
    """Test hook management functions."""

    def test_install_hooks_sets_excepthook(self):
        """Test that install_hooks sets sys.excepthook."""
        original_hook = sys.excepthook
        reporter = Reporter(enabled=True)
        reporter.enable()

        install_hooks(reporter)

        assert sys.excepthook != original_hook
        assert sys.excepthook is not None

        # Cleanup
        uninstall_hooks()

    def test_install_hooks_sets_thread_excepthook(self):
        """Test that install_hooks sets threading.excepthook."""
        original_hook = threading.excepthook
        reporter = Reporter(enabled=True)
        reporter.enable()

        install_hooks(reporter)

        assert threading.excepthook != original_hook
        assert threading.excepthook is not None

        # Cleanup
        uninstall_hooks()

    def test_uninstall_hooks_restores_original(self):
        """Test that uninstall_hooks restores original hooks."""
        original_excepthook = sys.excepthook
        original_thread_excepthook = threading.excepthook

        reporter = Reporter(enabled=True)
        reporter.enable()
        install_hooks(reporter)

        # Verify hooks are installed
        assert sys.excepthook != original_excepthook
        assert threading.excepthook != original_thread_excepthook

        uninstall_hooks()

        # Verify hooks are restored
        assert sys.excepthook == original_excepthook
        assert threading.excepthook == original_thread_excepthook

    def test_is_hooks_installed_false_initially(self):
        """Test that is_hooks_installed returns False initially."""
        uninstall_hooks()  # Ensure clean state
        assert not is_hooks_installed()

    def test_is_hooks_installed_true_after_install(self):
        """Test that is_hooks_installed returns True after install."""
        reporter = Reporter(enabled=True)
        reporter.enable()
        install_hooks(reporter)

        assert is_hooks_installed()

        # Cleanup
        uninstall_hooks()

    def test_is_hooks_installed_false_after_uninstall(self):
        """Test that is_hooks_installed returns False after uninstall."""
        reporter = Reporter(enabled=True)
        reporter.enable()
        install_hooks(reporter)
        assert is_hooks_installed()

        uninstall_hooks()
        assert not is_hooks_installed()

    def test_exception_handler_calls_reporter(self):
        """Test that exception handler calls reporter."""
        mock_reporter = Mock()
        mock_reporter.enabled = True

        install_hooks(mock_reporter)

        # Simulate an exception
        try:
            raise ValueError("test exception")
        except ValueError as e:
            sys.excepthook(type(e), e, e.__traceback__)

        # Verify reporter was called
        mock_reporter.report_exception.assert_called_once()

        # Cleanup
        uninstall_hooks()

    def test_thread_exception_handler_calls_reporter(self):
        """Test that thread exception handler calls reporter."""
        mock_reporter = Mock()
        mock_reporter.enabled = True

        install_hooks(mock_reporter)

        # Create exception hook args
        try:
            raise ValueError("test exception")
        except ValueError as e:
            args = threading.ExceptHookArgs(
                exc_type=type(e),
                exc_value=e,
                exc_traceback=e.__traceback__,
                thread=None,
            )
            threading.excepthook(args)

        # Verify reporter was called
        mock_reporter.report_exception.assert_called_once()

        # Cleanup
        uninstall_hooks()

    def test_exception_handler_preserves_original_behavior(self):
        """Test that exception handler calls original hook."""
        original_called = []

        def original_hook(exc_type, exc_value, exc_tb):
            original_called.append(True)

        sys.excepthook = original_hook

        reporter = Reporter(enabled=True)
        reporter.enable()
        install_hooks(reporter)

        # Simulate an exception
        try:
            raise ValueError("test")
        except ValueError as e:
            sys.excepthook(type(e), e, e.__traceback__)

        # Verify original hook was called
        assert len(original_called) > 0

        # Cleanup
        uninstall_hooks()
