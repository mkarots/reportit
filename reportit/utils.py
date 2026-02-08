"""Utility functions for exception formatting and thread information."""

import json
import threading
import traceback
from datetime import datetime
from typing import Any, Dict, Optional, Type


def format_exception(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_traceback: Optional[Any],
) -> str:
    """
    Format exception traceback as a string.

    Args:
        exc_type: Exception type.
        exc_value: Exception value.
        exc_traceback: Exception traceback.

    Returns:
        Formatted traceback string.
    """
    return "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))


def get_thread_info() -> Dict[str, Any]:
    """
    Get information about the current thread.

    Returns:
        Dictionary with thread name and ID.
    """
    thread = threading.current_thread()
    return {
        "thread_name": thread.name,
        "thread_id": thread.ident,
        "is_main_thread": thread is threading.main_thread(),
    }


def create_exception_payload(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_traceback: Optional[Any],
    scope: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a structured exception payload.

    Args:
        exc_type: Exception type.
        exc_value: Exception value.
        exc_traceback: Exception traceback.
        scope: Optional scope identifier (e.g., function name, module).

    Returns:
        Dictionary containing structured exception information.
    """
    traceback_str = format_exception(exc_type, exc_value, exc_traceback)
    thread_info = get_thread_info()

    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "exception_type": exc_type.__name__,
        "exception_message": str(exc_value),
        "traceback": traceback_str,
        "thread_info": thread_info,
    }

    if scope:
        payload["scope"] = scope

    return payload


def format_payload_as_json(payload: Dict[str, Any]) -> str:
    """
    Format payload as JSON string.

    Args:
        payload: Exception payload dictionary.

    Returns:
        JSON-formatted string.
    """
    return json.dumps(payload, indent=2)


def format_payload_as_text(payload: Dict[str, Any]) -> str:
    """
    Format payload as human-readable text.

    Args:
        payload: Exception payload dictionary.

    Returns:
        Human-readable text string.
    """
    lines = [
        f"Exception Report - {payload['timestamp']}",
        "=" * 60,
        f"Type: {payload['exception_type']}",
        f"Message: {payload['exception_message']}",
    ]

    if "scope" in payload:
        lines.append(f"Scope: {payload['scope']}")

    thread_info = payload["thread_info"]
    lines.extend(
        [
            f"Thread: {thread_info['thread_name']} (ID: {thread_info['thread_id']})",
            f"Main Thread: {thread_info['is_main_thread']}",
            "",
            "Traceback:",
            "-" * 60,
            payload["traceback"],
            "=" * 60,
            "",
        ]
    )

    return "\n".join(lines)
