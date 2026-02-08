"""Bridge implementations for exception reporting output."""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

from reportit.utils import format_payload_as_json, format_payload_as_text


class Bridge(ABC):
    """Abstract base class for exception reporting bridges."""

    @abstractmethod
    def send(self, payload: Dict[str, Any]) -> None:
        """
        Send exception payload to the bridge destination.

        Args:
            payload: Exception payload dictionary.

        Raises:
            Exception: If sending fails (implementation-specific).
        """
        pass


class FileBridge(Bridge):
    """Bridge that writes exceptions to a log file."""

    def __init__(self, log_file: str = ".cursor/exceptions.log"):
        """
        Initialize file bridge.

        Args:
            log_file: Path to the log file.
        """
        self.log_file = log_file
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Ensure the log file directory exists."""
        directory = os.path.dirname(self.log_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def send(self, payload: Dict[str, Any]) -> None:
        """
        Write exception payload to log file.

        Args:
            payload: Exception payload dictionary.
        """
        try:
            text_output = format_payload_as_text(payload)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(text_output)
        except OSError:
            # Silently fail to avoid interfering with application
            # In production, you might want to log this to stderr
            pass


class HTTPBridge(Bridge):
    """Bridge that sends exceptions via HTTP POST."""

    def __init__(self, endpoint: str = "http://localhost:7331/exception"):
        """
        Initialize HTTP bridge.

        Args:
            endpoint: HTTP endpoint URL.
        """
        self.endpoint = endpoint

    def send(self, payload: Dict[str, Any]) -> None:
        """
        Send exception payload via HTTP POST.

        Args:
            payload: Exception payload dictionary.
        """
        try:
            json_data = format_payload_as_json(payload).encode("utf-8")
            request = Request(
                self.endpoint,
                data=json_data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            # Use a short timeout to avoid blocking
            with urlopen(request, timeout=1.0) as response:
                # Response is read but not used
                _ = response.read()
        except (URLError, OSError, ValueError):
            # Silently fail to avoid interfering with application
            # In production, you might want to log this to stderr
            pass


def create_bridges(
    bridge_type: str,
    http_endpoint: Optional[str] = None,
    log_file: Optional[str] = None,
) -> list[Bridge]:
    """
    Create bridge instances based on bridge type.

    Args:
        bridge_type: Type of bridge ("file", "http", or "both").
        http_endpoint: HTTP endpoint URL (for http/both).
        log_file: Log file path (for file/both).

    Returns:
        List of bridge instances.
    """
    bridges: list[Bridge] = []

    if bridge_type in ("file", "both"):
        file_bridge = FileBridge(log_file=log_file or ".cursor/exceptions.log")
        bridges.append(file_bridge)

    if bridge_type in ("http", "both"):
        http_bridge = HTTPBridge(
            endpoint=http_endpoint or "http://localhost:7331/exception"
        )
        bridges.append(http_bridge)

    return bridges
