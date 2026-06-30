# Billing Dispute Resolution

> **TL;DR:** Customers raise billing disputes via the in-app **Dispute** button on any invoice line, which opens a billing ticket with the line in question pre-attached. Investigation is owned by the billing specialist; resolution targets are 5 business days for line-item adjustments and 10 business days for chargeback responses to the card network.

## What counts as a dispute

A billing dispute is a customer assertion that an invoice line is incorrect, unauthorized, or contractually disallowed. The most common categories are:

- **Duplicate charge.** Two identical line items on the same invoice. Often caused by a provisioning replay (see [kb-0002-understanding-invoice-line-items.md](kb-0002-understanding-invoice-line-items.md)) but sometimes a real billing bug — investigate before refunding.
- **Pro-ration miscalculation.** A mid-cycle plan change pro-rated incorrectly. Confirm the upgrade/downgrade event date in the audit log against the line's pro-ration period.
- **Seat overcounting.** The seat count on the invoice exceeds the maximum concurrent users in the billing period. Pull the seat-history report from **Reports → Billing → Seat Activity** to verify.
- **Unauthorized charge.** A line for a feature/SKU the customer claims they did not enable. Check the activation audit log; the customer may have authorized via SSO without realizing.

Disputes outside these categories (e.g., "the invoice is correct but I want a discount") are NOT disputes — route those to the account team for commercial discussion.

## Resolution workflow

1. The dispute ticket lands with category `billing` and priority `high`. The billing specialist reviews within 1 business day and posts an acknowledgement to the customer.
2. The specialist gathers evidence: the disputed invoice, the audit-log entries for any state changes during the billing period, and the seat/usage reports if relevant.
3. If the customer is correct, the specialist issues a credit memo via the billing portal. Credit memos appear on the next invoice as a negative line and reduce the next charge. **Refunds to the original payment method require finance approval and a separate ticket.**
4. If the customer is incorrect, the specialist sends a written explanation with links to the relevant audit-log entries. The ticket stays open for 5 business days to allow customer rebuttal before being closed.
5. If the dispute escalates to a card-network chargeback (Visa/Mastercard/Amex notify us 1-3 business days after the customer files), the billing specialist drafts a chargeback response with the same evidence. The 10-business-day card-network deadline is hard — past it, we lose by default.

## Refund vs credit memo

The default remediation is a **credit memo** applied to the next invoice. Credit memos are processed in our billing system without involving payment networks, so they are fast and reversible.

**Refunds to the original payment method** require finance approval and have a 5-business-day processing window after approval. Open a separate ticket in the `finance` queue (not the customer-facing support queue) with the dispute ticket linked. Reasons that warrant a refund instead of a credit:

- The customer has cancelled their account and will not have a future invoice to apply the credit to.
- The customer is on an annual contract that has been paid in full and has 6+ months remaining (apply the credit to the renewal instead unless the customer specifically requests refund).
- A regulatory requirement (consumer-protection law in the customer's jurisdiction) mandates refund.

## Common errors

- **"Cannot issue credit memo — invoice in disputed state"** — the invoice is locked because a chargeback was filed by the card network. The credit memo path is unavailable until the chargeback resolves; respond to the chargeback first.
- **Customer disputes a line they themselves provisioned** — happens about 30% of the time. Send the audit log entry showing the action, the user who took it, and the timestamp. This usually closes the ticket quickly.
- **Dispute aged past 60 days** — our standard SLA covers disputes raised within 60 days of the invoice. Beyond that, escalate to a senior billing specialist for a one-off determination.

## Related articles

- [kb-0002-understanding-invoice-line-items.md](kb-0002-understanding-invoice-line-items.md)
- [kb-0005-seat-provisioning-and-removal.md](kb-0005-seat-provisioning-and-removal.md)
- [kb-0011-data-retention-policy.md](kb-0011-data-retention-policy.md)
