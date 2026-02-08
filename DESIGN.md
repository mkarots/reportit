# Exception Reporting Library Design Document

## One-sentence summary

A Python library that intercepts uncaught exceptions and thread exceptions, forwarding structured crash reports to Cursor IDE via configurable bridges (file or HTTP).

## 1. Overview

### What

A lightweight exception reporting library that hooks into Python's exception handling system (`sys.excepthook` and `threading.excepthook`) to automatically capture and report uncaught exceptions. Reports are sent to Cursor IDE via configurable bridges: file-based logging or HTTP POST.

### Why

Developers working in Cursor IDE need a way to automatically capture exceptions without manual copy-pasting of tracebacks. This library provides automatic exception interception with zero code changes required in the application logic.

### When to use

- During development and debugging in Cursor IDE
- When you want automatic exception capture without modifying application code
- When you need exception reporting from background threads
- When you want dev-only exception reporting (disabled in production by default)

## 2. Non-Goals

- **Not responsible for**: Catching exceptions that are already handled by `try/except` blocks
- **Not responsible for**: Exception recovery or retry logic
- **Not responsible for**: Production error monitoring (this is dev-only by design)
- **Out of scope**: Exception filtering or rate limiting
- **Out of scope**: Exception aggregation or analytics

## 3. Key Concepts & Terminology

| Term | Meaning |
|------|---------|
| Bridge | Output mechanism for exception reports (file or HTTP) |
| Hook | Python's exception interception mechanism (`sys.excepthook`, `threading.excepthook`) |
| Reporter | Core class that formats exceptions and routes them to bridges |
| Config | Configuration management for bridge selection and environment detection |
| Payload | Structured exception data (type, message, traceback, thread info) |

## 4. High-Level Design

### Main components

1. **Hooks Module** (`hooks.py`): Installs and manages exception hooks
2. **Reporter Class** (`reporter.py`): Formats exceptions and routes to bridges
3. **Bridge Abstractions** (`bridges.py`): Abstract base class and concrete implementations
4. **Configuration** (`config.py`): Environment variable detection and bridge selection
5. **Utilities** (`utils.py`): Exception formatting and thread information extraction

### Data flow

1. Uncaught exception occurs in application code
2. Python calls `sys.excepthook` (or `threading.excepthook` for threads)
3. Hook handler calls Reporter's `report_exception()` method
4. Reporter formats exception into structured payload
5. Reporter sends payload to all configured bridges
6. Bridges output payload (file write or HTTP POST)
7. Original exception handler is called (preserves normal behavior)

### Key invariants

- Original exception behavior is always preserved
- Bridge failures never propagate to application
- Reporting only occurs when explicitly enabled
- Bridges are created at root level (dependency injection)

## 5. API / Interface

### Public API

**Function: `enable()`**

Input:
- `bridge`: Optional bridge type ("file", "http", "both")
- `http_endpoint`: Optional HTTP endpoint URL
- `log_file`: Optional log file path
- `enabled`: Optional override for environment variable

Output: None (side effect: installs hooks)

**Function: `disable()`**

Input: None

Output: None (side effect: uninstalls hooks)

**Class: `Reporter`**

Input:
- `bridges`: List of Bridge instances (required for root composition)
- `config`: Optional Config instance

Methods:
- `enable()`: Enable reporting
- `disable()`: Disable reporting
- `report_exception()`: Manually report an exception

## 6. Happy Path Example

**Step 1**: Developer enables reporting
```python
from reportit import enable
enable()  # Checks CURSOR_EXCEPTION_REPORTING env var
```

**Step 2**: Application code raises uncaught exception
```python
def process_data():
    result = 1 / 0  # Uncaught ZeroDivisionError
```

**Step 3**: Exception is automatically intercepted
- Hook handler captures exception
- Reporter formats payload
- Bridges write to file or send HTTP POST

**Step 4**: Exception appears in `.cursor/exceptions.log` or HTTP endpoint
- Structured format with timestamp, traceback, thread info
- Original exception still prints to stderr (normal behavior)

**Result**: Developer sees exception in Cursor without manual copy-paste.

## 7. Edge Cases & Failure Modes

### What can fail?

- **Bridge failures**: File write permissions, HTTP endpoint unreachable
- **Hook conflicts**: Multiple libraries installing hooks
- **Thread exceptions**: Exceptions in background threads
- **Configuration errors**: Invalid bridge type or endpoint URL

### How failures are handled

- **Bridge failures**: Silently ignored (failures don't propagate to application)
- **Hook conflicts**: Original hooks are preserved and called after reporting
- **Thread exceptions**: Handled via `threading.excepthook` with thread context
- **Configuration errors**: Defaults to file bridge, validates at enable time

### What the system guarantees

- Original exception behavior is always preserved
- Application never crashes due to reporting failures
- Thread-safe exception reporting
- Zero performance impact when disabled

## 8. Constraints & Assumptions

### Performance limits

- HTTP bridge uses 1-second timeout (non-blocking)
- File bridge uses append mode (no locking)
- No rate limiting (assumes dev-only usage)

### Security assumptions

- HTTP endpoint is localhost only (dev environment)
- File bridge writes to project directory (assumes trusted environment)
- No authentication required (dev-only tool)

### Environmental requirements

- Python 3.8+
- Write access to log file directory (for file bridge)
- Network access to HTTP endpoint (for HTTP bridge, optional)

## 9. Alternatives Considered

**Option A: Logging-based interception** — Rejected because requires application code changes and doesn't catch uncaught exceptions.

**Option B: Decorator-based approach** — Rejected because requires manual decoration of every function, doesn't scale.

**Option C: Context manager approach** — Rejected because only works for explicit code blocks, doesn't catch all exceptions.

**Option D: Current hook-based approach** — Selected because zero code changes required, catches all uncaught exceptions automatically.

## 10. Open Questions

**Q1**: Should we support exception filtering (e.g., ignore certain exception types)?

**Q2**: Should we add rate limiting for high-frequency exceptions?

**Q3**: Should we support custom payload formatters?

**Q4**: Should we add metrics/analytics for exception frequency?

## 11. Appendix

### Architecture Diagram

```
Application Code
    │
    ├─> Uncaught Exception
    │       │
    │       ▼
    └─> sys.excepthook / threading.excepthook
            │
            ▼
        Hook Handler (hooks.py)
            │
            ▼
        Reporter (reporter.py)
            │
            ├─> Format Payload (utils.py)
            │
            ▼
        Bridges (bridges.py)
            │
            ├─> FileBridge ──> .cursor/exceptions.log
            │
            └─> HTTPBridge ──> POST localhost:7331/exception
```

### Root Composition Pattern

Concrete class instantiation follows root composition principle:

- **Root**: `enable()` function in `__init__.py` creates bridges
- **Dependency Injection**: Bridges injected into Reporter constructor
- **Abstraction**: Reporter depends on Bridge interface, not concrete classes

This enables:
- Easy testing (mock bridges)
- Extensibility (new bridge types without Reporter changes)
- Testability (isolate components)
