import structlog

from support_api.logging import configure_logging

configure_logging(json_output=False)
log = structlog.get_logger()

log.info(
    "ticket_classified",
    ticket_id="TKT-10001",
    priority="urgent",
    category="billing",
    confidence=0.94
)

log.warning(
    "enrichment_slow",
    ticket_id="TKT-10001",
    duration_ms=3520
)

