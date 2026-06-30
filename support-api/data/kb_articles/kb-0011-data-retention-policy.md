# Data Retention Policy

> **TL;DR:** Customer data is retained for the lifetime of the active subscription plus 90 days after cancellation, after which it is hard-deleted. Audit logs are retained for 7 years for regulatory reasons even after customer-data deletion. Customers on Enterprise plans can request a custom retention schedule via their account manager.

## Default retention windows

| Data category | Active subscription | Post-cancellation hold | After hold |
|---|---|---|---|
| Tickets, messages, attachments | Indefinite | 90 days | Hard-deleted |
| Customer + user profile records | Indefinite | 90 days | Hard-deleted |
| Audit logs (security-relevant events) | Indefinite | Indefinite | Retained 7 years from event |
| Telemetry (latency, error counts) | Indefinite | 30 days | Hard-deleted |
| Backups | 30 days rolling | 30 days from cancellation | Hard-deleted |

The 90-day post-cancellation hold gives customers time to reactivate or request a final data export. Hard-delete is a destructive operation with no undo; we run it once daily and confirm completion in the audit log.

## Customer-initiated deletion (right to erasure)

EU GDPR, California CCPA, and several other jurisdictions grant individuals the right to request deletion of their personal data on demand. The platform supports this via the **Settings → Privacy → Delete My Data** button (for end-users) and via the `DELETE /v1/customers/{id}/personal-data` API call (for admins acting on a user's behalf).

Important constraints on right-to-erasure requests:

- The deletion is partial. Personal-identifying fields (name, email, phone, profile photo, free-text bio) are nulled out; the underlying ticket/comment/audit records remain with the user identifier replaced by a one-way hash. This preserves system integrity (foreign-key relationships, audit log continuity) while removing personally identifiable content.
- Audit-log entries for security-relevant events (sign-in, permission changes, data exports) are NOT deleted — they are retained for 7 years per our regulatory commitments. The user identifier in those logs is also hashed.
- Once submitted, the request is logged and processed within 30 days as required by GDPR Article 17. Most requests complete within 24 hours.

## Holds and exceptions

Three situations pause the standard retention timeline:

1. **Legal hold.** If the platform receives a subpoena, court order, or formal litigation-hold request affecting a customer's data, all retention timers for that data freeze until legal counsel releases the hold. Customers are notified unless the hold itself is sealed.
2. **Open dispute or chargeback.** Billing data tied to an open dispute (see [kb-0010-billing-dispute-resolution.md](kb-0010-billing-dispute-resolution.md)) is held until the dispute resolves — we may need it to respond to a card-network chargeback.
3. **Customer-requested extended retention.** Enterprise customers can negotiate longer retention via their MSA. The custom schedule is recorded in the contract metadata and overrides the table above.

## Data export before deletion

Customers should export their data before requesting deletion if they want to retain it. The export tool is at **Settings → Data Export** and produces a ZIP containing:

- All tickets, comments, and attachments as JSON + the original attachment files.
- Customer + user records as JSON.
- Audit logs filtered to the requesting customer's tenant as CSV.

Exports are generated asynchronously (typically 5-30 minutes for a large tenant) and are available for download for 7 days. After 7 days the export ZIP is hard-deleted from our object store.

See [kb-0007-data-export-csv-formats.md](kb-0007-data-export-csv-formats.md) for column conventions in the CSV outputs.

## Common errors

- **"Cannot delete — customer has active subscription"** — cancel the subscription first, then the 90-day hold begins. The button is greyed out for active accounts to prevent accidental destruction.
- **"Audit log retention conflict"** — you tried to delete a recent (under-7-year) audit-log entry. Audit-log records are immutable to satisfy compliance commitments; this is by design and cannot be overridden.
- **"Export already in progress"** — only one export per tenant runs at a time. Wait for the current one to complete (visible in **Settings → Data Export → History**) before queuing another.

## Related articles

- [kb-0007-data-export-csv-formats.md](kb-0007-data-export-csv-formats.md)
- [kb-0010-billing-dispute-resolution.md](kb-0010-billing-dispute-resolution.md)
- [kb-0009-api-token-rotation-and-scopes.md](kb-0009-api-token-rotation-and-scopes.md)
