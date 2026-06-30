"""A Decorator factor for timing all functions in support-api"""

from contextlib import contextmanager
from functools import wraps
from pathlib import Path
import time
import structlog
import os

_log = structlog.get_logger(__name__)

# @timed()
def timed(label: str | None = None): # factory
    """Log the wall-clock duration of any decorated callables.

    Usage - '@timed()' (parens are required) or 'timed(label="custom-name")'
    The optional label overrides the functions qualified name in the log event.
    """

    def decorator(func): # decorator
        event_label = label or func.__qualname__

        @wraps(func)
        def wrapper(*args, **kwargs): # replaces the decorator w/ func call
            started = time.perf_counter()
            try:
                return func(*args, **kwargs) # compute(1_000_000)
            finally:
                duration_ms = round((time.perf_counter() - started) * 1000, 2)
                _log.info("timed", label=event_label, duration_ms=duration_ms)
        
        return wrapper
    
    return decorator


# __enter__ and __exit__ functions included for you w/ contextmanager
@contextmanager
def atomic_write(path: Path, encoding: str = "utf-8"):
    """Write to a tempfile next to 'path', then rename the file on clean exit.

    On exception, the tempfile is removed and the original file is left untouched.
    Callers get a writable file handle as the 'as' value

    ContextManager -> generator

    support-api/src/support_api/utils.py.tmp

    """
    tmp = path.with_suffix(path.suffix + ".tmp")

    try:
        with tmp.open("w", encoding=encoding) as file:
            yield file

    except BaseException:
        if tmp.exists():
            tmp.unlink()
        raise

    else:
        os.replace(tmp, path)