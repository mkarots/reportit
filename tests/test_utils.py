"""Tests for utils module."""

import json
import threading
from datetime import datetime

import pytest

from reportit.utils import (
    format_exception,
    get_thread_info,
    create_exception_payload,
    format_payload_as_json,
    format_payload_as_text,
)


class TestFormatException:
    """Test format_exception function."""

    def test_format_exception_basic(self):
        """Test formatting a basic exception."""
        try:
            raise ValueError("test error")
        except ValueError as e:
            result = format_exception(type(e), e, e.__traceback__)
            assert "ValueError" in result
            assert "test error" in result
            assert "Traceback" in result or "traceback" in result.lower()

    def test_format_exception_with_none_traceback(self):
        """Test formatting exception with None traceback."""
        exc = ValueError("test")
        result = format_exception(ValueError, exc, None)
        assert "ValueError" in result
        assert "test" in result


class TestGetThreadInfo:
    """Test get_thread_info function."""

    def test_get_thread_info_returns_dict(self):
        """Test that get_thread_info returns a dictionary."""
        info = get_thread_info()
        assert isinstance(info, dict)
        assert "thread_name" in info
        assert "thread_id" in info
        assert "is_main_thread" in info

    def test_get_thread_info_main_thread(self):
        """Test thread info for main thread."""
        info = get_thread_info()
        assert info["is_main_thread"] is True
        assert info["thread_name"] == threading.main_thread().name

    def test_get_thread_info_custom_thread(self):
        """Test thread info for custom thread."""
        thread_info_list = []

        def worker():
            thread_info_list.append(get_thread_info())

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()

        assert len(thread_info_list) == 1
        info = thread_info_list[0]
        assert info["is_main_thread"] is False
        assert info["thread_id"] is not None


class TestCreateExceptionPayload:
    """Test create_exception_payload function."""

    def test_create_payload_basic(self):
        """Test creating a basic exception payload."""
        try:
            raise ValueError("test error")
        except ValueError as e:
            payload = create_exception_payload(type(e), e, e.__traceback__)

            assert isinstance(payload, dict)
            assert payload["exception_type"] == "ValueError"
            assert payload["exception_message"] == "test error"
            assert "timestamp" in payload
            assert "traceback" in payload
            assert "thread_info" in payload

    def test_create_payload_with_scope(self):
        """Test creating payload with scope."""
        try:
            raise ValueError("test")
        except ValueError as e:
            payload = create_exception_payload(
                type(e), e, e.__traceback__, scope="test_function"
            )

            assert payload["scope"] == "test_function"

    def test_create_payload_has_timestamp(self):
        """Test that payload includes timestamp."""
        try:
            raise ValueError("test")
        except ValueError as e:
            payload = create_exception_payload(type(e), e, e.__traceback__)

            # Verify timestamp is valid ISO format
            timestamp = payload["timestamp"]
            assert timestamp.endswith("Z")
            # Should be parseable
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


class TestFormatPayloadAsJSON:
    """Test format_payload_as_json function."""

    def test_format_payload_as_json(self):
        """Test formatting payload as JSON."""
        payload = {
            "exception_type": "ValueError",
            "exception_message": "test",
            "timestamp": "2024-01-01T00:00:00Z",
        }

        json_str = format_payload_as_json(payload)
        assert isinstance(json_str, str)

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["exception_type"] == "ValueError"


class TestFormatPayloadAsText:
    """Test format_payload_as_text function."""

    def test_format_payload_as_text(self):
        """Test formatting payload as text."""
        payload = {
            "exception_type": "ValueError",
            "exception_message": "test error",
            "timestamp": "2024-01-01T00:00:00Z",
            "traceback": "Traceback (most recent call last):\n  ...",
            "thread_info": {
                "thread_name": "MainThread",
                "thread_id": 12345,
                "is_main_thread": True,
            },
        }

        text = format_payload_as_text(payload)

        assert "Exception Report" in text
        assert "ValueError" in text
        assert "test error" in text
        assert "MainThread" in text
        assert "Traceback" in text

    def test_format_payload_as_text_with_scope(self):
        """Test formatting payload with scope."""
        payload = {
            "exception_type": "ValueError",
            "exception_message": "test",
            "timestamp": "2024-01-01T00:00:00Z",
            "scope": "test_function",
            "traceback": "...",
            "thread_info": {
                "thread_name": "MainThread",
                "thread_id": 12345,
                "is_main_thread": True,
            },
        }

        text = format_payload_as_text(payload)
        assert "Scope: test_function" in text
