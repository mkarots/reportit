"""Exception reporting library for Cursor IDE integration."""

from pathlib import Path
from typing import Any, Optional, Type

from reportit.bridges import create_bridges
from reportit.config import BridgeType, Config
from reportit.hooks import install_hooks, is_hooks_installed, uninstall_hooks
from reportit.reporter import Reporter

# Read version from package metadata or pyproject.toml
_DEFAULT_VERSION = "0.1.0"
try:
    from importlib.metadata import PackageNotFoundError, version

    try:
        __version__ = version("reportit")
    except PackageNotFoundError:
        # Package not installed, read from pyproject.toml
        _pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        if _pyproject_path.exists():
            try:
                # Python 3.11+ has tomllib in stdlib
                import tomllib

                with open(_pyproject_path, "rb") as f:
                    _pyproject = tomllib.load(f)
                    __version__ = _pyproject["project"]["version"]
            except ImportError:
                # Python < 3.11, try tomli (optional dev dependency)
                try:
                    import tomli as tomllib  # type: ignore[import-untyped]

                    with open(_pyproject_path, "rb") as f:
                        _pyproject = tomllib.load(f)
                        __version__ = _pyproject["project"]["version"]
                except ImportError:
                    # Fallback if tomli not available
                    __version__ = _DEFAULT_VERSION
            except (KeyError, FileNotFoundError):
                __version__ = _DEFAULT_VERSION
        else:
            __version__ = _DEFAULT_VERSION
except ImportError:
    # Python < 3.8 (shouldn't happen given requires-python >= 3.8)
    __version__ = _DEFAULT_VERSION

# Global reporter instance for convenience functions
_global_reporter: Optional[Reporter] = None


def enable(
    bridge: Optional[BridgeType] = None,
    http_endpoint: Optional[str] = None,
    log_file: Optional[str] = None,
    enabled: Optional[bool] = None,
) -> None:
    """
    Enable exception reporting with default configuration.

    This is a convenience function that creates a Reporter instance,
    enables it, and installs the exception hooks. Bridges are created
    at the root level (here) following root composition principle.

    Args:
        bridge: Bridge type to use ("file", "http", or "both").
                If None, uses default from config.
        http_endpoint: HTTP endpoint URL. If None, uses default.
        log_file: Log file path. If None, uses default.
        enabled: Whether reporting is enabled. If None, checks environment variable.
    """
    global _global_reporter

    # Create config
    config = Config(
        enabled=enabled,
        bridge=bridge,
        http_endpoint=http_endpoint,
        log_file=log_file,
    )

    # Create bridges at root level (root composition)
    bridges = create_bridges(
        bridge_type=config.bridge,
        http_endpoint=config.http_endpoint,
        log_file=config.log_file,
    )

    # Create reporter with bridges injected (dependency injection)
    _global_reporter = Reporter(
        bridges=bridges,
        config=config,
    )

    # Enable and install hooks
    _global_reporter.enable()
    install_hooks(_global_reporter)


def disable() -> None:
    """Disable exception reporting and uninstall hooks."""
    global _global_reporter

    uninstall_hooks()

    if _global_reporter:
        _global_reporter.disable()
        _global_reporter = None


def report_exception(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_traceback: Optional[Any],
    scope: Optional[str] = None,
) -> None:
    """
    Manually report an exception.

    Args:
        exc_type: Exception type.
        exc_value: Exception value.
        exc_traceback: Exception traceback.
        scope: Optional scope identifier.
    """
    if _global_reporter:
        _global_reporter.report_exception(exc_type, exc_value, exc_traceback, scope)


# Export main classes and functions
__all__ = [
    "enable",
    "disable",
    "report_exception",
    "Reporter",
    "Config",
    "BridgeType",
    "install_hooks",
    "uninstall_hooks",
    "is_hooks_installed",
    "__version__",
]
