# Resetting Your Account Password

> **TL;DR:** Use the "Forgot password?" link on the sign-in page to trigger a reset email. The reset link is valid for 30 minutes. If you have 2FA enabled, you will need access to your second factor to complete the sign-in after the password change.

## When to use password reset vs. admin intervention

Self-service password reset works for any user with a verified email address on their account. If your email address has changed or you no longer have access to it, self-service will not work and a tenant administrator must reset the password on your behalf from the Users console. Users whose accounts are locked due to failed sign-in attempts (five consecutive failures) must also wait for admin intervention or for the 30-minute lockout window to expire.

## Step-by-step reset flow

1. Navigate to the sign-in page and click **Forgot password?** below the password field.
2. Enter the email address associated with your account and click **Send reset link**. You should receive an email within 60 seconds from `no-reply@support-platform.com`.
3. Open the email and click **Reset password**. The link opens a browser page where you can enter a new password. Password requirements: minimum 14 characters, at least one uppercase, one lowercase, one digit, one symbol, and not in our common-password blocklist.
4. After submitting the new password, you will be redirected to the sign-in page. Use your new password to sign in. If you have 2FA enabled, you will be prompted for your second factor as usual.

## The reset link expired - what now?

Reset links expire after **30 minutes** from the moment the email is sent. If the link has expired, you will see a page that says "This reset link is no longer valid." Simply click **Forgot password?** again to generate a new one. The most common causes of expired-link frustration are: (a) the email sat in a filtered inbox for longer than 30 minutes, (b) the user clicked a stale link from a previous reset attempt, or (c) the link was clicked on a device with an incorrect system clock. If you are repeatedly seeing expired-link errors, check your spam folder and consider whitelisting `no-reply@support-platform.com`.

## 2FA considerations

Password reset does **not** reset or bypass 2FA. If you have lost access to your 2FA device, you must contact your tenant administrator to reset the 2FA factor separately. Admin-initiated 2FA reset is audit-logged and may require identity verification depending on your tenant's security posture. After a 2FA reset, the next sign-in will prompt you to re-enroll a new second factor.

## Common errors

- **"Email not found"** — the address you entered is not associated with any active account. Double-check spelling and that you are using your work email, not a personal one.
- **"Too many reset requests"** — you can request up to 5 reset emails per hour per account. Wait an hour or contact your admin.
- **Reset link redirects to a login loop** — typically a cookie/cache issue. Try an incognito window or clear cookies for the sign-in domain.

## Related articles

- [kb-0005-seat-provisioning-and-removal.md](kb-0005-seat-provisioning-and-removal.md)
- [kb-0004-sso-enablement-for-enterprise.md](kb-0004-sso-enablement-for-enterprise.md)
- [kb-0008-troubleshooting-slow-dashboards.md](kb-0008-troubleshooting-slow-dashboards.md)
