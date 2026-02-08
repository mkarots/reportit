# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-01

### Added

- Initial release of reportit exception reporting library
- Core Reporter class for exception reporting
- FileBridge for writing exceptions to log files
- HTTPBridge for sending exceptions via HTTP POST
- Configuration management via Config class
- Environment variable support (`CURSOR_EXCEPTION_REPORTING`)
- Hook management for `sys.excepthook` and `threading.excepthook`
- Exception formatting utilities (JSON and text formats)
- Thread information extraction
- Comprehensive unit tests
- Integration tests
- Documentation (README.md and DESIGN.md)
- Root composition pattern implementation (bridges created at root level)
- Makefile for project management tasks
- Ruff and Black configuration in pyproject.toml
- Project badges in README.md

### Features

- Automatic interception of uncaught exceptions
- Thread exception handling
- Dual bridge support (file and HTTP)
- Dev-only activation via environment variable
- Non-intrusive design (preserves original exception behavior)
- Thread-safe exception reporting
- Dependency injection support for testing (bridges can be injected into Reporter)

### Architecture

- Follows SOLID principles throughout
- Root composition: concrete classes instantiated only at root (`enable()` function)
- Dependency injection: Reporter accepts bridges via constructor
- Abstract Bridge interface enables extensibility

### Development

- Makefile with common tasks (test, lint, format, install, build)
- Ruff linting configuration
- Black code formatting configuration
- Pytest with coverage reporting
