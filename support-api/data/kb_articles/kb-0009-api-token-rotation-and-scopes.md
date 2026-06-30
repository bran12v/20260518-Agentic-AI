# API Token Rotation and Scopes

> **TL;DR:** Service-account API tokens should be rotated every 90 days. Tokens are scope-bound at creation — you cannot widen a token's scopes after issue. To rotate without downtime, issue the new token first, deploy the new credential, then revoke the old token within the 14-day overlap window.

## Token types and where they apply

The platform supports three distinct token types and they are not interchangeable.

- **User personal access tokens (PATs)** are tied to an individual user's identity. They expire when the user is deactivated or when the PAT itself reaches its expiry date (90 days max). PATs inherit the user's role-based permissions; you cannot grant a PAT scopes beyond what the user already has.
- **Service-account tokens** belong to a tenant-level service account, not a person. They are the right choice for CI/CD pipelines, ETL jobs, and any background automation. Service-account tokens have explicit scope grants set at creation and survive personnel changes.
- **OAuth bearer tokens** are short-lived (1 hour) and are issued by our OAuth endpoint after a refresh-token exchange. Use these for end-user-facing integrations where the user has authorized your app.

If you are unsure which to use, the rule of thumb is: a human will sign in → PAT or OAuth; an unattended process will run → service-account token.

## How scopes work

Scopes are deny-by-default. A token with no scopes can only call `/healthz` and `/auth/whoami`. Common scopes include `tickets:read`, `tickets:write`, `customers:read`, `webhooks:manage`, `kb:read`, and `admin:tenant`. Each scope is documented in the API reference under the endpoint that requires it. You cannot widen scopes on an existing token — issue a new token with the desired scope set and revoke the old one.

The most common scope mistake is granting `admin:tenant` to an automation that only needs `tickets:write`. `admin:tenant` includes user provisioning and billing endpoints; if the token leaks, the blast radius is dramatically larger. **Apply least privilege at issue time.**

## Zero-downtime rotation procedure

1. In the **Settings → API Tokens** page, click **Issue New Token**. Enter a descriptive name including the rotation date (e.g., `etl-pipeline-2026-04`).
2. Select the same scope set as the token you are rotating. Click **Create**. Copy the token value immediately — it is shown once and never again.
3. Deploy the new token to your secret store (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault). Update your application configuration to read the new secret name.
4. Roll your application instances. Confirm via your monitoring that requests are succeeding under the new token.
5. Once stable for at least 24 hours, return to the API Tokens page and click **Revoke** on the old token. The old token is invalidated within 60 seconds across all regions.

The platform enforces a maximum overlap window of **14 days** — after 14 days, the old token is automatically revoked even if you have not pressed the button. This is to prevent forgotten-but-still-valid tokens from accumulating.

## Common errors

- **"Invalid scope for this endpoint" (403)** — the token lacks a required scope. Check the API reference for the endpoint and confirm the scope is in the token's scope list. Issue a new token if needed.
- **"Token expired" (401)** — the token has passed its expiry date. Issue a new one and update your application.
- **"Token revoked" (401)** — someone explicitly revoked the token, or the 14-day overlap window expired. Check the audit log under **Settings → Audit** to see who/when.

## Related articles

- [kb-0004-sso-enablement-for-enterprise.md](kb-0004-sso-enablement-for-enterprise.md)
- [kb-0001-resetting-account-password.md](kb-0001-resetting-account-password.md)
- [kb-0006-webhook-delivery-and-retries.md](kb-0006-webhook-delivery-and-retries.md)
