import logging
import os
import sys

import structlog

def configure_logging(
    *,
    level: str | None = None, 
    json_output: bool | None = None
) -> None:
    """Idempotent global logger configuration.

    LOG_LEVEL - stdlib level name (debug/info/warning/...) Default: info
    LOG_JSON=1 - force JSON output. Default: JSON if stderr is non-TTY
    """
    log_level_name = (level or os.environ.get("LOG_LEVEL", "info")).upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    if json_output is None:
        json_output = (
            os.environ.get("LOG_JSON", "").lower() in {"1", "true", "yes"}
            or not sys.stderr.isatty()
        )
    
    renderer = (
        structlog.processors.JSONRenderer()
        if json_output
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            renderer
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        cache_logger_on_first_use=True
    )
    logging.basicConfig(level=log_level, format="%(message)s", stream=sys.stderr)