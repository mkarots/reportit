"""Tests for config module."""

import os
import pytest
from unittest.mock import patch

from reportit.config import Config, get_default_config


class TestConfig:
    """Test Config class."""

    def test_default_config_disabled(self):
        """Test that default config is disabled when env var is not set."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            assert not config.enabled

    def test_config_enabled_from_env_true(self):
        """Test config enabled when env var is 'true'."""
        with patch.dict(os.environ, {"CURSOR_EXCEPTION_REPORTING": "true"}):
            config = Config()
            assert config.enabled

    def test_config_enabled_from_env_1(self):
        """Test config enabled when env var is '1'."""
        with patch.dict(os.environ, {"CURSOR_EXCEPTION_REPORTING": "1"}):
            config = Config()
            assert config.enabled

    def test_config_enabled_from_env_yes(self):
        """Test config enabled when env var is 'yes'."""
        with patch.dict(os.environ, {"CURSOR_EXCEPTION_REPORTING": "yes"}):
            config = Config()
            assert config.enabled

    def test_config_enabled_from_env_on(self):
        """Test config enabled when env var is 'on'."""
        with patch.dict(os.environ, {"CURSOR_EXCEPTION_REPORTING": "on"}):
            config = Config()
            assert config.enabled

    def test_config_disabled_from_env_false(self):
        """Test config disabled when env var is 'false'."""
        with patch.dict(os.environ, {"CURSOR_EXCEPTION_REPORTING": "false"}):
            config = Config()
            assert not config.enabled

    def test_config_explicit_enabled(self):
        """Test config with explicit enabled=True."""
        config = Config(enabled=True)
        assert config.enabled

    def test_config_explicit_disabled(self):
        """Test config with explicit enabled=False."""
        config = Config(enabled=False)
        assert not config.enabled

    def test_config_explicit_overrides_env(self):
        """Test that explicit enabled overrides environment variable."""
        with patch.dict(os.environ, {"CURSOR_EXCEPTION_REPORTING": "true"}):
            config = Config(enabled=False)
            assert not config.enabled

    def test_default_bridge(self):
        """Test default bridge type."""
        config = Config()
        assert config.bridge == "file"

    def test_custom_bridge(self):
        """Test custom bridge type."""
        config = Config(bridge="http")
        assert config.bridge == "http"

    def test_both_bridge(self):
        """Test 'both' bridge type."""
        config = Config(bridge="both")
        assert config.bridge == "both"

    def test_default_http_endpoint(self):
        """Test default HTTP endpoint."""
        config = Config()
        assert config.http_endpoint == "http://localhost:7331/exception"

    def test_custom_http_endpoint(self):
        """Test custom HTTP endpoint."""
        config = Config(http_endpoint="http://example.com/report")
        assert config.http_endpoint == "http://example.com/report"

    def test_default_log_file(self):
        """Test default log file path."""
        config = Config()
        assert config.log_file == ".cursor/exceptions.log"

    def test_custom_log_file(self):
        """Test custom log file path."""
        config = Config(log_file="/tmp/exceptions.log")
        assert config.log_file == "/tmp/exceptions.log"

    def test_use_file_bridge_file(self):
        """Test use_file_bridge returns True for 'file' bridge."""
        config = Config(bridge="file")
        assert config.use_file_bridge()
        assert not config.use_http_bridge()

    def test_use_file_bridge_both(self):
        """Test use_file_bridge returns True for 'both' bridge."""
        config = Config(bridge="both")
        assert config.use_file_bridge()
        assert config.use_http_bridge()

    def test_use_http_bridge_http(self):
        """Test use_http_bridge returns True for 'http' bridge."""
        config = Config(bridge="http")
        assert config.use_http_bridge()
        assert not config.use_file_bridge()

    def test_get_default_config(self):
        """Test get_default_config function."""
        with patch.dict(os.environ, {}, clear=True):
            config = get_default_config()
            assert isinstance(config, Config)
            assert not config.enabled
