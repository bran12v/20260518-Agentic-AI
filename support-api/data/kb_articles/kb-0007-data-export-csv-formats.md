# Data Export: CSV and JSON Formats, Streaming for Large Exports

> **TL;DR:** The `/api/v2/exports` endpoint creates an async export job. Small exports (under 100 MB) can be downloaded as a single file; larger ones must use the streaming endpoint. CSV is the default; JSON is available for callers who prefer typed output. Scheduled recurring exports are configured separately under **Admin → Exports → Schedules**.

## Creating an export job

Exports are asynchronous. The API call returns immediately with a job id; you poll (or listen for the `export.completed` webhook) to know when the file is ready.

```bash
curl -X POST https://api.support-platform.com/api/v2/exports \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset": "tickets",
    "format": "csv",
    "date_range": {"start": "2026-01-01", "end": "2026-03-31"},
    "filters": {"tenant": "acme-corp", "status": ["resolved", "closed"]},
    "include_conversation": false
  }'
```

Response:

```json
{
  "export_id": "exp_7c3a8d1f9b",
  "status": "queued",
  "created_at": "2026-04-21T14:03:21Z",
  "estimated_rows": 48921
}
```

Available datasets: `tickets`, `customers`, `conversation_turns`, `usage_events`, `audit_log`.

## Polling and downloading

Poll `GET /api/v2/exports/<export_id>` until `status` is `completed` or `failed`. On completion the response includes a signed download URL valid for 6 hours:

```json
{
  "export_id": "exp_7c3a8d1f9b",
  "status": "completed",
  "row_count": 48921,
  "bytes": 287654321,
  "download_url": "https://exports.support-platform.com/...signed...",
  "expires_at": "2026-04-21T20:14:07Z"
}
```

If the export is larger than 100 MB, the response will also include `streaming_url` — use that instead; see the next section.

## Streaming for large exports

Single-file downloads over ~500 MB reliably fail because upstream proxies and browsers impose timeouts. For large exports, use the streaming endpoint:

```
GET /api/v2/exports/<export_id>/stream
Accept: text/csv  (or application/x-ndjson for NDJSON)
```

The streaming endpoint returns the file as a chunked transfer-encoded response. Clients should consume the stream row-by-row and write to disk. This pattern works for any size — 10 GB exports stream cleanly in about 20-30 minutes.

A Python client:

```python
import httpx
with httpx.stream("GET", f"{API}/api/v2/exports/{eid}/stream") as r:
    with open("export.csv", "wb") as f:
        for chunk in r.iter_bytes(chunk_size=65536):
            f.write(chunk)
```

If your existing job was created without the stream flag and its download 502s, you do not need to re-create the job — just swap to the streaming URL for the same export id.

## CSV vs JSON vs NDJSON

- **CSV** (`format: "csv"`) — default. Best for spreadsheet tools and BI loaders. One header row, one row per record. Nested fields are flattened with dotted paths (`customer.name`). Arrays are serialized as JSON strings inside cells.
- **JSON** (`format: "json"`) — a single JSON array of objects. Easy to work with programmatically; bad for very large exports because you cannot stream-parse a single array.
- **NDJSON** (`format: "ndjson"`) — newline-delimited JSON, one record per line. The best format for large streaming exports processed in pipelines.

## Schema stability

Export schemas are versioned. The default is the latest stable schema; pass `schema_version: "2026-04-01"` to pin an older schema. **Breaking changes are announced at least 60 days in advance** in release notes and via the `export.schema_deprecated` webhook. If a field you depend on has disappeared, check the deprecation notices — you may need to pin a schema version or update your consumer.

## Scheduled recurring exports

Set up from **Admin → Exports → Schedules**. You can target:

- A destination (signed URL email, SFTP, S3-compatible bucket)
- A cron-style schedule (e.g., `0 6 * * 1` for 6am every Monday)
- A dataset + filters + format combination

Scheduled exports produce `export.completed` webhooks identical to one-off exports.

## Common errors

- **`400 invalid_date_range`** — end date before start, or date range spans more than 365 days. Break into smaller ranges.
- **`403 export_quota_exceeded`** — you have hit the export-endpoint rate limit (10/hour). Wait or consolidate into fewer larger exports.
- **`502 Bad Gateway`** on download — use the streaming endpoint instead (see above).

## Related articles

- [kb-0003-api-rate-limits-and-429.md](kb-0003-api-rate-limits-and-429.md)
- [kb-0006-webhook-delivery-and-retries.md](kb-0006-webhook-delivery-and-retries.md)
- [kb-0008-troubleshooting-slow-dashboards.md](kb-0008-troubleshooting-slow-dashboards.md)
