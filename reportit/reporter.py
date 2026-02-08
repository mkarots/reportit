"""Core Reporter class for exception reporting."""

from typing import Any, List, Optional, Type

from reportit.bridges import Bridge
from reportit.config import BridgeType, Config
from reportit.utils import create_exception_payload


class Reporter:
    """Handles exception reporting to configured bridges."""

    def __init__(
        self,
        bridges: Optional[List[Bridge]] = None,
        enabled: Optional[bool] = None,
        bridge: Optional[BridgeType] = None,
        http_endpoint: Optional[str] = None,
        log_file: Optional[str] = None,
        config: Optional[Config] = None,
    ):
        """
        Initialize the reporter.

        Args:
            bridges: Optional list of bridge instances. If None, bridges are created
                    from config. This allows dependency injection for testing.
            enabled: Whether reporting is enabled. If None, uses config default.
            bridge: Bridge type to use. If None, uses config default.
            http_endpoint: HTTP endpoint URL. If None, uses config default.
            log_file: Log file path. If None, uses config default.
            config: Optional Config instance. If provided, other args override it.
        """
        self._config = config or Config(
            enabled=enabled,
            bridge=bridge,
            http_endpoint=http_endpoint,
            log_file=log_file,
        )
        self._bridges: List[Bridge] = bridges or []
        self._enabled = False

    @property
    def enabled(self) -> bool:
        """Check if the reporter is enabled."""
        return self._enabled and self._config.enabled

    def enable(self) -> None:
        """Enable exception reporting."""
        if not self._config.enabled:
            return

        # Bridges should be provided via dependency injection or created at root
        # If not provided, this indicates improper usage (bridges should be created
        # at the root level, not here)
        if not self._bridges:
            raise RuntimeError(
                "Bridges must be provided via __init__ or created at root level. "
                "Use reportit.enable() or provide bridges parameter."
            )

        self._enabled = True

    def disable(self) -> None:
        """Disable exception reporting."""
        self._enabled = False

    def report_exception(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_traceback: Optional[Any],
        scope: Optional[str] = None,
    ) -> None:
        """
        Report an exception to all configured bridges.

        Args:
            exc_type: Exception type.
            exc_value: Exception value.
            exc_traceback: Exception traceback.
            scope: Optional scope identifier.
        """
        if not self.enabled:
            return

        try:
            payload = create_exception_payload(
                exc_type=exc_type,
                exc_value=exc_value,
                exc_traceback=exc_traceback,
                scope=scope,
            )

            for bridge in self._bridges:
                try:
                    bridge.send(payload)
                except Exception:
                    # Silently fail individual bridges to avoid cascading failures
                    pass
        except Exception:
            # Silently fail to avoid interfering with application
            pass
