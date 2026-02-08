"""Tests for bridges module."""

import json
import os
import tempfile
from unittest.mock import patch, MagicMock, Mock
from urllib.error import URLError

import pytest

from reportit.bridges import Bridge, FileBridge, HTTPBridge, create_bridges
from reportit.utils import create_exception_payload


class TestFileBridge:
    """Test FileBridge class."""

    def test_file_bridge_creates_directory(self):
        """Test that FileBridge creates directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "subdir", "exceptions.log")
            bridge = FileBridge(log_file=log_file)
            assert os.path.exists(os.path.dirname(log_file))

    def test_file_bridge_writes_payload(self):
        """Test that FileBridge writes exception payload to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "exceptions.log")
            bridge = FileBridge(log_file=log_file)

            payload = create_exception_payload(
                ValueError, ValueError("test error"), None
            )
            bridge.send(payload)

            assert os.path.exists(log_file)
            with open(log_file, "r") as f:
                content = f.read()
                assert "test error" in content
                assert "ValueError" in content

    def test_file_bridge_appends_multiple_exceptions(self):
        """Test that FileBridge appends multiple exceptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "exceptions.log")
            bridge = FileBridge(log_file=log_file)

            payload1 = create_exception_payload(
                ValueError, ValueError("error 1"), None
            )
            payload2 = create_exception_payload(
                TypeError, TypeError("error 2"), None
            )

            bridge.send(payload1)
            bridge.send(payload2)

            with open(log_file, "r") as f:
                content = f.read()
                assert content.count("Exception Report") == 2
                assert "error 1" in content
                assert "error 2" in content

    def test_file_bridge_handles_io_error_gracefully(self):
        """Test that FileBridge handles IO errors gracefully."""
        # Use a path that will cause permission error (on Unix)
        if os.name == "posix":
            bridge = FileBridge(log_file="/root/cannot_write.log")
            payload = create_exception_payload(
                ValueError, ValueError("test"), None
            )
            # Should not raise exception
            bridge.send(payload)


class TestHTTPBridge:
    """Test HTTPBridge class."""

    @patch("reportit.bridges.urlopen")
    def test_http_bridge_sends_post_request(self, mock_urlopen):
        """Test that HTTPBridge sends POST request."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"OK"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        bridge = HTTPBridge(endpoint="http://localhost:7331/exception")
        payload = create_exception_payload(
            ValueError, ValueError("test error"), None
        )
        bridge.send(payload)

        assert mock_urlopen.called
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        assert request.get_method() == "POST"
        assert request.get_full_url() == "http://localhost:7331/exception"
        assert "application/json" in request.headers.get("Content-Type", "")

    @patch("reportit.bridges.urlopen")
    def test_http_bridge_sends_json_data(self, mock_urlopen):
        """Test that HTTPBridge sends JSON data."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"OK"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        bridge = HTTPBridge()
        payload = create_exception_payload(
            ValueError, ValueError("test error"), None
        )
        bridge.send(payload)

        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        data = request.data
        assert data is not None
        json_data = json.loads(data.decode("utf-8"))
        assert json_data["exception_type"] == "ValueError"
        assert json_data["exception_message"] == "test error"

    @patch("reportit.bridges.urlopen")
    def test_http_bridge_handles_url_error_gracefully(self, mock_urlopen):
        """Test that HTTPBridge handles URLError gracefully."""
        mock_urlopen.side_effect = URLError("Connection refused")

        bridge = HTTPBridge()
        payload = create_exception_payload(
            ValueError, ValueError("test"), None
        )
        # Should not raise exception
        bridge.send(payload)

    @patch("reportit.bridges.urlopen")
    def test_http_bridge_uses_timeout(self, mock_urlopen):
        """Test that HTTPBridge uses timeout."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"OK"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        bridge = HTTPBridge()
        payload = create_exception_payload(
            ValueError, ValueError("test"), None
        )
        bridge.send(payload)

        call_kwargs = mock_urlopen.call_args[1]
        assert "timeout" in call_kwargs
        assert call_kwargs["timeout"] == 1.0


class TestCreateBridges:
    """Test create_bridges function."""

    def test_create_file_bridge(self):
        """Test creating file bridge."""
        bridges = create_bridges("file", log_file="/tmp/test.log")
        assert len(bridges) == 1
        assert isinstance(bridges[0], FileBridge)
        assert bridges[0].log_file == "/tmp/test.log"

    def test_create_http_bridge(self):
        """Test creating HTTP bridge."""
        bridges = create_bridges("http", http_endpoint="http://example.com/report")
        assert len(bridges) == 1
        assert isinstance(bridges[0], HTTPBridge)
        assert bridges[0].endpoint == "http://example.com/report"

    def test_create_both_bridges(self):
        """Test creating both bridges."""
        bridges = create_bridges(
            "both",
            http_endpoint="http://example.com/report",
            log_file="/tmp/test.log",
        )
        assert len(bridges) == 2
        assert isinstance(bridges[0], FileBridge)
        assert isinstance(bridges[1], HTTPBridge)

    def test_create_bridges_defaults(self):
        """Test creating bridges with defaults."""
        bridges = create_bridges("file")
        assert len(bridges) == 1
        assert isinstance(bridges[0], FileBridge)
        assert bridges[0].log_file == ".cursor/exceptions.log"

        bridges = create_bridges("http")
        assert len(bridges) == 1
        assert isinstance(bridges[0], HTTPBridge)
        assert bridges[0].endpoint == "http://localhost:7331/exception"
