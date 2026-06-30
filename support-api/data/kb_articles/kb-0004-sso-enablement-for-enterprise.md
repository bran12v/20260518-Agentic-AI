# Enabling SAML SSO for Enterprise Tenants

> **TL;DR:** SSO is available on Enterprise plans. You will exchange SAML metadata with your IdP (Okta, Azure AD, Ping, or any SAML 2.0 provider), configure attribute mappings, verify the domain you are federating, and enable SSO enforcement in stages. Budget one working session with your IdP admin — most enablements complete in 45-60 minutes.

## Prerequisites

Before starting, confirm:

- Your tenant is on an Enterprise plan. Business and Starter cannot federate.
- You have **tenant admin** privileges on the support platform.
- You have admin access to your Identity Provider (IdP). SAML 2.0 is required; OIDC is on the roadmap but not yet available.
- You have verified the email domain you intend to federate (see `kb-0005-seat-provisioning-and-removal.md` for domain verification).
- You have a maintenance window agreed with your user base — enabling enforcement disrupts active sessions.

## Step 1 — Generate and download our SP metadata

Navigate to **Admin → Security → Single Sign-On** and click **Configure SAML**. The platform will display your Service Provider details:

- **SP Entity ID:** `urn:support-platform:tenant:<your-tenant-id>`
- **ACS URL:** `https://auth.support-platform.com/saml/acs/<your-tenant-id>`
- **Single Logout URL:** `https://auth.support-platform.com/saml/slo/<your-tenant-id>`

Download the SP metadata XML from the **Download SP Metadata** button. You will upload this into your IdP in the next step.

## Step 2 — Create the application in your IdP

In your IdP, create a new SAML 2.0 application. Upload the SP metadata XML or paste the values manually. Configure the following attribute mappings — these are required and the SSO handshake will reject assertions that omit any of them:

| SAML attribute | Maps to | Notes |
|----------------|---------|-------|
| `NameID` (Format: emailAddress) | user email | Must be the canonical email on record |
| `givenName` | first name | |
| `sn` | last name | |
| `groups` (optional) | role sync | See role mapping below |

Sign the assertion. We require signed assertions; unsigned responses are rejected. We accept `RSA-SHA256` and `RSA-SHA512`.

## Step 3 — Upload IdP metadata to the platform

Back in the platform, paste the IdP metadata XML (or provide the metadata URL for automatic refresh). Click **Validate metadata**. The validator checks the signing certificate, entity ID, and issuer against the URLs in the XML. Any mismatch here is almost always the wrong metadata file pasted in the wrong direction — SP metadata goes to the IdP, IdP metadata comes to the platform.

## Step 4 — Test with a single user before enforcing

Use the **Test SSO** button with an admin account that has a password fallback. This runs a full assertion round-trip and displays the parsed assertion so you can verify attribute mappings are correct. Do this before enabling enforcement for the tenant. A successful test produces a "SSO test successful" banner and the assertion payload is shown for inspection.

## Step 5 — Enable enforcement in stages

Enforcement has three modes:

- **Optional** — users can sign in with either SSO or password. Good for the rollout period.
- **Required for most users** — SSO required except for listed break-glass admin accounts.
- **Required for all** — SSO required with no exceptions. Recommended steady state.

Always leave at least one break-glass account on password authentication. Losing SSO (expired IdP cert, misconfigured mapping) with no password fallback locks your entire tenant out.

## Role mapping (optional)

If you include `groups` attribute in your assertions, you can configure **Admin → Security → Role Mapping** to map IdP group names to platform roles. This enables just-in-time provisioning: a user signing in via SSO for the first time whose groups match a configured mapping is auto-provisioned into the correct role.

## Common failures

- **"Invalid signature"** — assertion is signed with a certificate that does not match the one in IdP metadata. Usually a cert rotation that was not pushed to the platform.
- **"Missing required attribute: NameID"** — attribute mappings in the IdP application are incomplete.
- **"User not provisioned"** — SSO assertion arrived for a user whose email is not on your tenant. Either enable just-in-time provisioning, or pre-provision the user before they sign in.

## Related articles

- [kb-0001-resetting-account-password.md](kb-0001-resetting-account-password.md)
- [kb-0005-seat-provisioning-and-removal.md](kb-0005-seat-provisioning-and-removal.md)
