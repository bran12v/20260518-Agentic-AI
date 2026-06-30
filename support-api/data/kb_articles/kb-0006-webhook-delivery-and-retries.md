# Webhook Delivery, Signing, and Retries

> **TL;DR:** Webhooks are HTTP POST callbacks to an endpoint you register, signed with HMAC-SHA256. Every delivery includes an `X-Webhook-Signature` header. Failed deliveries retry on an exponential schedule for up to 24 hours; after that, events are dropped to a dead-letter log you can replay from the admin console.

## Events you can subscribe to

Available event types as of the 2026-04-15 platform update:

- `ticket.created` — a new ticket has been filed
- `ticket.updated` — any field on a ticket changed (status, priority, assignee, tags, etc.)
- `ticket.resolved` — status transitioned to `resolved`
- `conversation_turn.created` — a new customer message, agent reply, or internal note was added
- `customer.created` — a new customer record was added to your tenant
- `customer.plan_changed` — a plan upgrade/downgrade occurred
- `export.completed` — an async export job finished and is ready to download

Subscribe from **Admin → Developers → Webhooks → Create endpoint**. Provide your callback URL (must be HTTPS) and select the events. You may register up to 10 endpoints per tenant.

## Signing and verification

Every request includes these headers:

- `X-Webhook-Signature: t=<unix-ts>,v1=<hex-hmac>` — HMAC-SHA256 of `<timestamp>.<raw-body>` using your endpoint's signing secret
- `X-Webhook-Event: ticket.updated` — event type
- `X-Webhook-Delivery-Id: <uuid>` — unique id for this delivery attempt
- `X-Webhook-Event-Id: <uuid>` — stable id for the underlying event, identical across retries

To verify:

```python
import hmac, hashlib

def verify(secret: bytes, signature_header: str, raw_body: bytes) -> bool:
    parts = dict(p.split("=", 1) for p in signature_header.split(","))
    ts, v1 = parts["t"], parts["v1"]
    signed = f"{ts}.".encode() + raw_body
    expected = hmac.new(secret, signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, v1)
```

Reject requests older than 5 minutes (timestamp comparison) to defeat replay attacks. The signing algorithm was updated on 2026-04-15 from the previous `X-Signature: sha256=<hex>` format to the timestamped `t=...,v1=...` format above — if your verification started failing around that date, you are probably still on the old format.

## Retry schedule

We consider a delivery successful only on a `2xx` response within 10 seconds. Anything else — `3xx`, `4xx`, `5xx`, timeout, TLS error, DNS failure — is retried on this schedule:

| Attempt | Delay after previous |
|---------|----------------------|
| 1 (initial) | — |
| 2 | 30 seconds |
| 3 | 2 minutes |
| 4 | 10 minutes |
| 5 | 1 hour |
| 6 | 6 hours |
| 7 (final) | 17 hours |

Total window: ~24 hours. After the 7th attempt, the event moves to **dead-letter** status.

## Dead-letter handling

Dead-lettered events are visible at **Admin → Developers → Webhooks → Dead Letter Queue** for 30 days. From there you can:

- Inspect the payload and delivery attempts (status codes, response bodies, timing)
- **Replay** — re-queue the event for fresh delivery attempts
- **Drop** — explicitly discard

If your endpoint was down for longer than 24 hours and you are staring at hundreds of dead-lettered events, bulk replay is supported up to 1,000 events per click.

## "I'm receiving ticket.created but not ticket.updated"

Check three things in order:

1. **Subscription.** In the webhook endpoint configuration, confirm `ticket.updated` is in the events list. A common bug is subscribing to `ticket.created` only and expecting update delivery.
2. **Filters.** If you configured event filters (e.g., only `tenant=acme-corp` or only `priority=urgent`), your updates may be filtered out. Check the endpoint's filter config.
3. **Delivery log.** **Admin → Developers → Webhooks → <endpoint> → Delivery log** shows every delivery attempt including rejections. If the log shows zero attempts for `ticket.updated`, the subscription is the problem. If it shows attempts with 4xx responses, your endpoint is rejecting them — inspect those.

## Related articles

- [kb-0003-api-rate-limits-and-429.md](kb-0003-api-rate-limits-and-429.md)
- [kb-0007-data-export-csv-formats.md](kb-0007-data-export-csv-formats.md)
