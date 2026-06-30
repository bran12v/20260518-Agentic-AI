# Seat Provisioning and Removal

> **TL;DR:** Tenant admins can add, remove, and reassign seats from **Admin → Users**. Each seat corresponds to one authenticated user. Removing a seat does not delete the user's historical data — their authored tickets and comments remain, but they can no longer sign in. Overage is charged for active users above your plan's included seat count; "active" means signed in at least once in the billing period.

## How seats are counted

Your plan includes a fixed number of seats (e.g., 45 seats on a Business plan). A seat is consumed for every user in one of these states:

- **Active** — signed in at least once during the current billing period
- **Invited** — invited within the past 30 days but has not accepted yet
- **Admin-reserved** — flagged by an admin as always-consuming regardless of activity

Users who have not signed in for 30+ days move to **Inactive** status and do not consume seats, though they remain visible in the directory. If they sign in again, they consume a seat and you may land in overage.

## Adding a user

1. Navigate to **Admin → Users → Add user**.
2. Enter the email address. The domain must be a verified domain on your tenant (see below).
3. Select the role: `member`, `power_user`, `admin`, or a custom role if your tenant has them configured.
4. Optionally assign to teams or projects.
5. Click **Send invite**. The user receives an email to set up their account (or complete SSO first-time sign-in if SSO is enforced).

Invites expire after 14 days. Re-send from the user's row in the directory if an invite has gone stale.

## Bulk seat provisioning

For onboarding more than ~10 users at once, use **Admin → Users → Bulk import** with a CSV in this format:

```csv
email,first_name,last_name,role,teams
alice@example.com,Alice,Smith,member,ops;claims
bob@example.com,Bob,Chen,admin,
```

The import is validated before execution. Errors (invalid domain, already-provisioned email, unknown role) are listed with their row numbers. After the validation step, an admin approves the import and invites are sent in a single batch.

## Removing a user

When an employee leaves, remove their seat the same day for two reasons: (1) security — revoking platform access, and (2) billing — freeing the seat immediately.

1. Navigate to **Admin → Users**, find the user, and click **Remove**.
2. Choose what to do with their owned objects (saved reports, scheduled exports, webhooks): reassign to another user, or leave as-is and the platform will mark them orphaned. Orphaned objects can be claimed later by an admin.
3. Confirm. The user's sessions are invalidated within 60 seconds and API keys issued under their identity are revoked.

Removal is soft-delete by default: the user record remains for 90 days so that audit trails still resolve their name. Hard-delete (GDPR-style removal of PII) is available via a separate data-subject request workflow.

## Domain verification for self-serve provisioning

Before you can add users from a domain, you must verify ownership. Navigate to **Admin → Security → Verified Domains**, add the domain, and publish the TXT record shown on the screen. DNS propagation is usually under an hour but may take up to 48 hours.

Verified domain required for:
- Self-serve user invites from that domain
- SSO federation (see `kb-0004-sso-enablement-for-enterprise.md`)
- Automatic user matching from IdP assertions

## Role changes

Role changes take effect on the user's next sign-in, or within 60 seconds if they are currently signed in (session is revalidated). Some roles are mutually exclusive (e.g., `admin` and `billing_only` cannot coexist) — the UI enforces this.

## Related articles

- [kb-0001-resetting-account-password.md](kb-0001-resetting-account-password.md)
- [kb-0004-sso-enablement-for-enterprise.md](kb-0004-sso-enablement-for-enterprise.md)
- [kb-0002-understanding-invoice-line-items.md](kb-0002-understanding-invoice-line-items.md)
