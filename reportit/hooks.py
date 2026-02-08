"""Hook management for exception interception."""

import sys
import threading
from typing import Any, Optional, Type

from reportit.reporter import Reporter

# Global state for hook management
_original_excepthook: Optional[Any] = None
_original_thread_excepthook: Optional[Any] = None
_reporter_instance: Optional[Reporter] = None


def _exception_handler(
    exc_type: Type[BaseException], exc_value: BaseException, exc_traceback: Any
) -> None:
    """
    Handle uncaught exceptions.

    Args:
        exc_type: Exception type.
        exc_value: Exception value.
        exc_traceback: Exception traceback.
    """
    # Report the exception
    if _reporter_instance:
        _reporter_instance.report_exception(exc_type, exc_value, exc_traceback)

    # Call original handler
    if _original_excepthook:
        _original_excepthook(exc_type, exc_value, exc_traceback)


def _thread_exception_handler(args: threading.ExceptHookArgs) -> None:
    """
    Handle exceptions in threads.

    Args:
        args: Exception hook arguments.
    """
    # Report the exception
    if _reporter_instance:
        _reporter_instance.report_exception(
            args.exc_type, args.exc_value, args.exc_traceback
        )

    # Call original handler if it exists
    if _original_thread_excepthook:
        _original_thread_excepthook(args)


def install_hooks(reporter: Reporter) -> None:
    """
    Install exception hooks.

    Args:
        reporter: Reporter instance to use for reporting exceptions.
    """
    global _original_excepthook, _original_thread_excepthook, _reporter_instance

    _reporter_instance = reporter

    # Save original hooks
    if _original_excepthook is None:
        _original_excepthook = sys.excepthook

    if _original_thread_excepthook is None:
        _original_thread_excepthook = threading.excepthook

    # Install new hooks
    sys.excepthook = _exception_handler
    threading.excepthook = _thread_exception_handler


def uninstall_hooks() -> None:
    """Uninstall exception hooks and restore original handlers."""
    global _original_excepthook, _original_thread_excepthook, _reporter_instance

    # Restore original hooks
    if _original_excepthook is not None:
        sys.excepthook = _original_excepthook
        _original_excepthook = None

    if _original_thread_excepthook is not None:
        threading.excepthook = _original_thread_excepthook
        _original_thread_excepthook = None

    _reporter_instance = None


def is_hooks_installed() -> bool:
    """
    Check if hooks are currently installed.

    Returns:
        True if hooks are installed, False otherwise.
    """
    return _reporter_instance is not None
