"""Configuration management for exception reporting."""

import os
from typing import Literal, Optional

BridgeType = Literal["file", "http", "both"]


class Config:
    """Manages configuration for exception reporting."""

    ENV_VAR_NAME = "CURSOR_EXCEPTION_REPORTING"
    DEFAULT_BRIDGE: BridgeType = "file"
    DEFAULT_HTTP_ENDPOINT = "http://localhost:7331/exception"
    DEFAULT_LOG_FILE = ".cursor/exceptions.log"

    def __init__(
        self,
        enabled: Optional[bool] = None,
        bridge: Optional[BridgeType] = None,
        http_endpoint: Optional[str] = None,
        log_file: Optional[str] = None,
    ):
        """
        Initialize configuration.

        Args:
            enabled: Whether reporting is enabled. If None, checks environment variable.
            bridge: Bridge type to use. If None, uses default.
            http_endpoint: HTTP endpoint URL. If None, uses default.
            log_file: Log file path. If None, uses default.
        """
        self._enabled = enabled
        self._bridge = bridge or self.DEFAULT_BRIDGE
        self._http_endpoint = http_endpoint or self.DEFAULT_HTTP_ENDPOINT
        self._log_file = log_file or self.DEFAULT_LOG_FILE

    @property
    def enabled(self) -> bool:
        """Check if exception reporting is enabled."""
        if self._enabled is not None:
            return self._enabled
        return self._is_enabled_from_env()

    @property
    def bridge(self) -> BridgeType:
        """Get the bridge type."""
        return self._bridge

    @property
    def http_endpoint(self) -> str:
        """Get the HTTP endpoint URL."""
        return self._http_endpoint

    @property
    def log_file(self) -> str:
        """Get the log file path."""
        return self._log_file

    @staticmethod
    def _is_enabled_from_env() -> bool:
        """Check if reporting is enabled via environment variable."""
        env_value = os.getenv(Config.ENV_VAR_NAME, "").lower()
        return env_value in ("true", "1", "yes", "on")

    def use_file_bridge(self) -> bool:
        """Check if file bridge should be used."""
        return self.bridge in ("file", "both")

    def use_http_bridge(self) -> bool:
        """Check if HTTP bridge should be used."""
        return self.bridge in ("http", "both")


def get_default_config() -> Config:
    """Get default configuration from environment."""
    return Config()
