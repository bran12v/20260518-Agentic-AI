# API Rate Limits and Handling 429 Responses

> **TL;DR:** Rate limits are enforced per-tenant per-endpoint using a sliding window. Business plans get 60 requests/minute on read endpoints and 20/minute on write endpoints. When limited, the API returns HTTP 429 with a `Retry-After` header (seconds). Clients must honor `Retry-After` and implement exponential backoff with jitter for 5xx responses.

## Published limits by plan

Rate limits are enforced at the tenant level, not per API key. All keys for a tenant share the same bucket.

| Plan | Read RPM | Write RPM | Burst capacity | Concurrent requests |
|------|----------|-----------|----------------|---------------------|
| Starter | 20 | 5 | 40 | 4 |
| Business | 60 | 20 | 120 | 16 |
| Enterprise | 600 | 120 | 1200 | 64 |

Read endpoints are `GET` requests; write endpoints are `POST`, `PATCH`, and `DELETE`. Bulk export endpoints (`/api/v2/exports/*`) have separate, lower limits because each export can produce significant downstream work — see the exports section below.

## The 429 response contract

When your tenant exceeds its rate limit, the API responds with HTTP status `429 Too Many Requests`. The response includes these headers:

- `Retry-After: <seconds>` — seconds until you may safely retry
- `X-RateLimit-Limit: <n>` — the ceiling for this window
- `X-RateLimit-Remaining: 0` — always zero when you receive a 429
- `X-RateLimit-Reset: <unix-timestamp>` — the moment the window resets

The response body is a structured error:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Tenant exceeded the 60 rpm limit for read endpoints.",
  "retry_after_seconds": 47,
  "window_reset_at": "2026-04-21T16:04:00Z"
}
```

## Recommended client behavior

1. **Always read `Retry-After`.** Do not guess. If the header says 47 seconds, do not retry before 47 seconds.
2. **On 5xx (500, 502, 503, 504), use exponential backoff with jitter.** Start at 1 second, double on each retry, cap at 30 seconds, add random jitter of 0-500ms to avoid thundering herd. Give up after 5 attempts.
3. **Do not retry on 4xx** (other than 429 and 408). 400, 401, 403, 404, 422 will return the same response no matter how many times you retry.
4. **Use request IDs.** Every response includes a `X-Request-ID` header. Log it. Include it when you open a support ticket.

A minimal Python pattern:

```python
import time, random, httpx

def call_with_retry(client, method, url, **kwargs):
    for attempt in range(5):
        r = client.request(method, url, **kwargs)
        if r.status_code == 429:
            wait = int(r.headers.get("Retry-After", "5"))
            time.sleep(wait)
            continue
        if r.status_code >= 500:
            backoff = min(30, 2 ** attempt) + random.random() * 0.5
            time.sleep(backoff)
            continue
        return r
    r.raise_for_status()
```

## "But I'm well under my limit and still getting 429"

Three common causes:

- **Burst vs sustained.** Business plans allow bursts up to 120 requests, but the sliding-window average must stay at or below 60 rpm. Firing 120 in the first 10 seconds of a minute will burn the burst allowance and leave you 429-limited for the remainder.
- **Shared-bucket surprise.** Remember all API keys on a tenant share the bucket. A background job running on a different server can push you over.
- **Export endpoints have a separate, lower limit** of 10 requests/hour for exports, regardless of plan. High-volume callers of `/api/v2/exports` should batch work into larger exports rather than many small ones.

## Related articles

- [kb-0006-webhook-delivery-and-retries.md](kb-0006-webhook-delivery-and-retries.md)
- [kb-0007-data-export-csv-formats.md](kb-0007-data-export-csv-formats.md)
- [kb-0002-understanding-invoice-line-items.md](kb-0002-understanding-invoice-line-items.md)
