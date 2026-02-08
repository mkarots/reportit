# reportit

Exception reporting library for Cursor IDE integration. Intercepts uncaught exceptions and thread exceptions. Forwards structured crash reports to Cursor via configurable bridges.

## Features

- **Automatic Exception Interception**: Catches uncaught exceptions via `sys.excepthook` and thread exceptions via `threading.excepthook`
- **Dual Bridge Support**: File-based logging (`.cursor/exceptions.log`) and HTTP endpoint (POST to localhost)
- **Dev-Only by Default**: Enabled via environment variable. Safe for production
- **Zero Dependencies**: Uses only Python standard library
- **Thread-Safe**: Handles exceptions from background threads with full context
- **Non-Intrusive**: Preserves original exception behavior. Fails silently if bridges fail

## Installation

```bash
pip install reportit
```

Or install from source:

```bash
git clone <repository-url>
cd reportit
pip install -e .
```

## Quick Start

### Simple One-Liner

Enable exception reporting with one line:

```python
from reportit import enable
enable()  # Checks CURSOR_EXCEPTION_REPORTING env var
```

### With Environment Variable

Set the environment variable, then enable:

```bash
export CURSOR_EXCEPTION_REPORTING=true
python your_script.py
```

```python
from reportit import enable
enable()  # Detects environment variable automatically
```

### Explicit Configuration

Configure bridges explicitly:

```python
from reportit import enable

# File bridge (default)
enable(bridge="file", log_file=".cursor/exceptions.log")

# HTTP bridge
enable(bridge="http", http_endpoint="http://localhost:7331/exception")

# Both bridges
enable(bridge="both")
```

## Usage

### Basic Usage

Enable reporting. Exceptions are captured automatically:

```python
from reportit import enable, disable

enable()

# Your code - exceptions are automatically reported
try:
    result = 1 / 0
except ZeroDivisionError:
    pass  # Exception already reported

# Disable when done (optional)
disable()
```

### Using Reporter Class Directly

Use Reporter class for advanced usage:

```python
from reportit import Reporter
from reportit.bridges import create_bridges
from reportit.config import Config

# Create bridges at root level
bridges = create_bridges("file", log_file=".cursor/exceptions.log")
config = Config(enabled=True)

# Create reporter with dependency injection
reporter = Reporter(bridges=bridges, config=config)
reporter.enable()

# Manually report an exception
try:
    raise ValueError("Something went wrong")
except ValueError as e:
    reporter.report_exception(type(e), e, e.__traceback__, scope="my_function")
```

### Thread Exception Handling

```python
import threading
from reportit import enable

enable()

def worker():
    raise RuntimeError("Thread exception")

thread = threading.Thread(target=worker)
thread.start()
thread.join()
# Exception is automatically reported
```

## Configuration

### Environment Variables

- `CURSOR_EXCEPTION_REPORTING`: Set to `true`, `1`, `yes`, or `on` to enable reporting

### Bridge Types

- **`file`** (default): Writes exceptions to a log file
- **`http`**: Sends exceptions via HTTP POST
- **`both`**: Uses both file and HTTP bridges

### Configuration Options

```python
enable(
    bridge="file",                    # Bridge type: "file", "http", or "both"
    http_endpoint="http://localhost:7331/exception",  # HTTP endpoint URL
    log_file=".cursor/exceptions.log",  # Log file path
    enabled=True                      # Override environment variable
)
```

## Exception Payload Format

Exceptions are reported in a structured format:

### JSON Format (HTTP Bridge)

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "exception_type": "ValueError",
  "exception_message": "Invalid input",
  "traceback": "Traceback (most recent call last):\n  ...",
  "thread_info": {
    "thread_name": "MainThread",
    "thread_id": 12345,
    "is_main_thread": true
  },
  "scope": "optional_scope_identifier"
}
```

### Text Format (File Bridge)

```
Exception Report - 2024-01-01T12:00:00Z
============================================================
Type: ValueError
Message: Invalid input
Scope: optional_scope_identifier
Thread: MainThread (ID: 12345)
Main Thread: True

Traceback:
------------------------------------------------------------
Traceback (most recent call last):
  ...
============================================================
```

## API Reference

### Functions

#### `enable(bridge=None, http_endpoint=None, log_file=None, enabled=None)`

Enable exception reporting and install hooks.

**Parameters:**
- `bridge`: Bridge type (`"file"`, `"http"`, or `"both"`). Default: `"file"`
- `http_endpoint`: HTTP endpoint URL. Default: `"http://localhost:7331/exception"`
- `log_file`: Log file path. Default: `".cursor/exceptions.log"`
- `enabled`: Override environment variable. If `None`, checks `CURSOR_EXCEPTION_REPORTING`

#### `disable()`

Disable exception reporting and uninstall hooks.

#### `report_exception(exc_type, exc_value, exc_traceback, scope=None)`

Manually report an exception.

**Parameters:**
- `exc_type`: Exception type (class)
- `exc_value`: Exception instance
- `exc_traceback`: Exception traceback object
- `scope`: Optional scope identifier (string)

### Classes

#### `Reporter`

Main reporter class for exception reporting.

**Methods:**
- `enable()`: Enable reporting and create bridges
- `disable()`: Disable reporting
- `report_exception(exc_type, exc_value, exc_traceback, scope=None)`: Report an exception

**Properties:**
- `enabled`: Whether reporting is currently enabled

#### `Config`

Configuration management class.

**Properties:**
- `enabled`: Whether reporting is enabled
- `bridge`: Bridge type
- `http_endpoint`: HTTP endpoint URL
- `log_file`: Log file path

## Architecture

The library follows SOLID principles:

- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: New bridge types can be added without modifying existing code
- **Liskov Substitution**: All bridges implement the same interface
- **Interface Segregation**: Minimal, focused interfaces
- **Dependency Inversion**: Reporter depends on Bridge abstraction, not concrete implementations

### Component Overview

```
┌─────────────┐
│   Hooks     │  Installs sys.excepthook and threading.excepthook
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Reporter   │  Formats exceptions and routes to bridges
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Bridges   │  FileBridge, HTTPBridge, or both
└─────────────┘
```

## Testing

Run tests with pytest:

```bash
pytest
```

With coverage:

```bash
pytest --cov=reportit --cov-report=html
```

## Development

### Setup

```bash
git clone <repository-url>
cd reportit
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

The code follows:
- SOLID principles
- PEP 8 style guidelines
- Comprehensive test coverage

## Limitations

- Only catches uncaught exceptions (exceptions that terminate the program or thread)
- Does not catch exceptions that are caught and handled by `try/except` blocks
- HTTP bridge requires a running server at the endpoint
- File bridge requires write permissions to the log file directory

## License

MIT License

## Contributing

Contributions are welcome! Please ensure:
- Code follows SOLID principles
- Tests are included for new features
- Code passes linting checks
