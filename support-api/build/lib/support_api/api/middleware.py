import time
import uuid

import structlog

from flask import Flask, Response, g, request

log = structlog.get_logger(__name__)

def register_request_logging(app: Flask) -> None:
    """Append or inject a pre-request correlation id in every request that comes thru the app."""
    # before
    @app.before_request # will run before every request
    def _start() -> None:
        id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:16] # da384-asdad3-asdaf3-asdad3-adsad3 example
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=id, method=request.method, path=request.path
        )
        g.request_id = id # g is a per request scratchpad
        g.start_time = time.perf_counter()

    # after
    @app.after_request # will run after every request
    def _end(response: Response) -> Response:
        duration_ms = round((time.perf_counter() - g.start_time) * 1000, 1)
        log.info(
            "request_completed",
            status=response.status_code,
            duration_ms=duration_ms
        )
        response.headers["X-Request-ID"] = g.request_id
        return response