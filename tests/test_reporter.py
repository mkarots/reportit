"""Tests for reporter module."""

import os
from unittest.mock import Mock, patch

import pytest

from reportit.bridges import create_bridges
from reportit.config import Config
from reportit.reporter import Reporter


class TestReporter:
    """Test Reporter class."""

    def test_reporter_disabled_by_default(self):
        """Test that reporter is disabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            bridges = create_bridges("file", log_file="/tmp/test.log")
            reporter = Reporter(bridges=bridges)
            assert not reporter.enabled

    def test_reporter_enabled_when_config_enabled(self):
        """Test that reporter is enabled when config is enabled."""
        bridges = create_bridges("file", log_file="/tmp/test.log")
        config = Config(enabled=True)
        reporter = Reporter(bridges=bridges, config=config)
        reporter.enable()
        assert reporter.enabled

    def test_reporter_enable_requires_bridges(self):
        """Test that enabling reporter requires bridges to be provided."""
        config = Config(enabled=True)
        reporter = Reporter(config=config)
        with pytest.raises(RuntimeError, match="Bridges must be provided"):
            reporter.enable()

    def test_reporter_enable_respects_config_disabled(self):
        """Test that reporter doesn't enable when config is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            bridges = create_bridges("file", log_file="/tmp/test.log")
            reporter = Reporter(bridges=bridges)
            reporter.enable()
            assert not reporter.enabled

    def test_reporter_disable(self):
        """Test disabling reporter."""
        bridges = create_bridges("file", log_file="/tmp/test.log")
        config = Config(enabled=True)
        reporter = Reporter(bridges=bridges, config=config)
        reporter.enable()
        assert reporter.enabled
        reporter.disable()
        assert not reporter.enabled

    def test_reporter_report_exception_when_disabled(self):
        """Test that reporter doesn't report when disabled."""
        bridges = create_bridges("file", log_file="/tmp/test.log")
        config = Config(enabled=True)
        reporter = Reporter(bridges=bridges, config=config)
        # Don't enable it
        assert not reporter.enabled

        # Mock bridges to verify they're not called
        mock_bridge = Mock()
        reporter._bridges = [mock_bridge]
        reporter.report_exception(ValueError, ValueError("test"), None)

        # Bridge should not be called
        mock_bridge.send.assert_not_called()

    def test_reporter_report_exception_when_enabled(self):
        """Test that reporter reports exceptions when enabled."""
        bridges = create_bridges("file", log_file="/tmp/test.log")
        config = Config(enabled=True)
        reporter = Reporter(bridges=bridges, config=config)
        reporter.enable()

        mock_bridge = Mock()
        reporter._bridges = [mock_bridge]

        reporter.report_exception(ValueError, ValueError("test"), None)

        mock_bridge.send.assert_called_once()
        payload = mock_bridge.send.call_args[0][0]
        assert payload["exception_type"] == "ValueError"
        assert payload["exception_message"] == "test"

    def test_reporter_report_exception_with_scope(self):
        """Test reporting exception with scope."""
        bridges = create_bridges("file", log_file="/tmp/test.log")
        config = Config(enabled=True)
        reporter = Reporter(bridges=bridges, config=config)
        reporter.enable()

        mock_bridge = Mock()
        reporter._bridges = [mock_bridge]

        reporter.report_exception(
            ValueError, ValueError("test"), None, scope="test_function"
        )

        payload = mock_bridge.send.call_args[0][0]
        assert payload["scope"] == "test_function"

    def test_reporter_handles_bridge_failure_gracefully(self):
        """Test that reporter handles bridge failures gracefully."""
        bridges = create_bridges("file", log_file="/tmp/test.log")
        config = Config(enabled=True)
        reporter = Reporter(bridges=bridges, config=config)
        reporter.enable()

        failing_bridge = Mock()
        failing_bridge.send.side_effect = Exception("Bridge error")
        reporter._bridges = [failing_bridge]

        # Should not raise exception
        reporter.report_exception(ValueError, ValueError("test"), None)

    def test_reporter_handles_multiple_bridges(self):
        """Test that reporter sends to all bridges."""
        bridges = create_bridges("both", log_file="/tmp/test.log")
        config = Config(enabled=True)
        reporter = Reporter(bridges=bridges, config=config)
        reporter.enable()

        assert len(reporter._bridges) == 2

        mock_bridge1 = Mock()
        mock_bridge2 = Mock()
        reporter._bridges = [mock_bridge1, mock_bridge2]

        reporter.report_exception(ValueError, ValueError("test"), None)

        mock_bridge1.send.assert_called_once()
        mock_bridge2.send.assert_called_once()

    def test_reporter_uses_custom_config(self):
        """Test that reporter uses custom config."""
        bridges = create_bridges("http")
        custom_config = Config(enabled=True, bridge="http")
        reporter = Reporter(bridges=bridges, config=custom_config)
        reporter.enable()

        assert reporter._config.bridge == "http"
        assert len(reporter._bridges) == 1

    def test_reporter_with_bridges_injection(self):
        """Test that reporter accepts bridges via dependency injection."""
        mock_bridge = Mock()
        config = Config(enabled=True)
        reporter = Reporter(bridges=[mock_bridge], config=config)
        reporter.enable()

        reporter.report_exception(ValueError, ValueError("test"), None)
        mock_bridge.send.assert_called_once()
