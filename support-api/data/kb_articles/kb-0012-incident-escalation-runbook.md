# Incident Escalation Runbook

> **TL;DR:** Customer-impacting incidents are classified Sev1–Sev4 by blast radius and customer impact. Sev1 (multi-tenant outage) pages on-call within 5 minutes; Sev3/Sev4 (single-tenant degradation, cosmetic issues) follow standard ticket flow. The on-call engineer owns the incident from declaration to resolution; the support specialist owns customer communication.

## Severity classification

| Severity | Definition | Page on-call? | Status-page update? |
|---|---|---|---|
| Sev1 | Platform-wide outage; >25% of tenants affected; primary feature unavailable | Yes — within 5 min | Yes — within 15 min |
| Sev2 | Significant degradation; one region down OR a major feature broken for many tenants | Yes — within 15 min | Yes — within 30 min |
| Sev3 | Single tenant or small set degraded; workaround exists | No — handle in business hours | No — direct message to affected tenants |
| Sev4 | Cosmetic issue; non-blocking; minor inconvenience | No | No |

**Misclassification is the most common runbook error.** When in doubt, classify upward — a Sev2 that turns out to be Sev3 costs an unnecessary page; a Sev3 that turns out to be Sev1 costs trust.

## Sev1 / Sev2 escalation steps

1. The first responder (could be customer support, on-call SRE, or whoever notices) declares the incident in `#incidents` Slack with the format: `INCIDENT DECLARED Sev{1,2}: <one-line description>. Page=<yes/no>. Status page=<yes/no>.`
2. The PagerDuty escalation policy `platform-oncall` fires within 5 minutes. The primary on-call acknowledges within 5 minutes; if no acknowledgement, the secondary on-call is paged at 10 minutes.
3. The on-call engineer creates a Zoom incident bridge and posts the link in `#incidents`. Customer support, comms, and engineering leads join.
4. **Communication ownership separates from technical ownership immediately.** The on-call engineer focuses on diagnosis and remediation. The on-call communications lead (named in `#incidents` channel topic) owns:
   - The status page update (statuspage.io component "Platform")
   - Customer-facing language in any tweet, email, or in-app banner
   - The incident's customer-support ticket (templated; see below)
5. Status-page updates land at minimum every 30 minutes during the incident, even if the message is "still investigating, no new information." Silence loses customer trust faster than bad news.
6. When the incident resolves, the comms lead posts the final status-page update (resolved, with a one-paragraph summary). The on-call engineer schedules a postmortem within 5 business days.

## Customer-support handling during an active incident

Support specialists fielding tickets during a Sev1/Sev2 do NOT investigate individually. The pattern is:

1. Confirm the incoming ticket relates to the active incident (symptoms match the status-page description, timeframe overlaps).
2. Reply with a copy-paste templated acknowledgement that links to the status page. Do not promise specific resolution times — defer to the status page.
3. Tag the ticket with the incident ID (Sev1/Sev2 incidents get auto-assigned IDs like `INC-2026-0042`).
4. Do not close the ticket until the incident itself resolves AND the customer's specific symptom has been verified resolved (a system-wide all-clear does not always reach every tenant simultaneously due to caching and rolling deploys).

If an incoming ticket APPEARS unrelated to the incident but the customer mentions related symptoms, escalate to the on-call comms lead — they will decide whether to broaden the incident scope.

## Sev3 / Sev4 handling (the standard path)

Sev3 issues follow the regular ticket flow. They land in the technical specialist queue with priority `high`. The specialist investigates within standard SLA (4 business hours for first response, 1 business day for resolution or escalation).

If a Sev3 investigation reveals the issue is broader than initially understood (e.g., what looked like a single-tenant problem is actually affecting many tenants), the specialist re-classifies upward and follows the Sev2 escalation path immediately. Re-classification is a normal part of incident handling — there is no penalty.

## Postmortems

Every Sev1 and Sev2 produces a postmortem within 5 business days. Postmortems are blameless: focus on the gaps in tooling/process/monitoring that allowed the incident to happen, not on individual decisions made under time pressure. The template lives at `runbooks/postmortem-template.md` in the engineering repo. Postmortems are shared with affected enterprise customers as part of our incident-response commitment.

## Common errors

- **Declaring an incident without paging on-call.** Sev1/Sev2 require paging — do not skip "because it's late" or "because it's the weekend." On-call rotations exist for exactly this.
- **Communicating before declaring.** Posting in a public Slack channel about a suspected incident before declaring it formally creates parallel narratives. Declare first, then communicate.
- **Closing a ticket too early.** During a Sev1/Sev2, the customer's symptom may resolve transiently and recur. Verify resolution by asking the customer to confirm, not by inferring from your own monitoring.

## Related articles

- [kb-0008-troubleshooting-slow-dashboards.md](kb-0008-troubleshooting-slow-dashboards.md)
- [kb-0006-webhook-delivery-and-retries.md](kb-0006-webhook-delivery-and-retries.md)
- [kb-0003-api-rate-limits-and-429.md](kb-0003-api-rate-limits-and-429.md)
