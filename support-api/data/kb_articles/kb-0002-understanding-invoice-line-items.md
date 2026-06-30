# Understanding Your Invoice Line Items

> **TL;DR:** Each invoice includes a base subscription charge, possible proration credits or debits from mid-cycle plan changes, usage overage line items (seats, API calls, storage), applied discounts, and tax. This article explains each line-item type and how to reconcile them against your order form.

## Base subscription charge

The base subscription charge is your contracted plan fee for the billing period. On monthly billing, it appears as `SUBSCRIPTION - <plan> - <month>` (e.g., `SUBSCRIPTION - Business - April 2026`). On annual billing, the full contract amount is charged once at the start of the annual term and does not reappear on subsequent monthly statements unless you add paid add-ons.

If your order form specified a custom discount (common on enterprise contracts), the discount is applied as a separate negative line item rather than reducing the base rate. This keeps the invoice auditable against the signed order form — if the discount percentage on your invoice does not match the percentage on your executed order form, open a billing ticket and attach the order form PDF.

## Prorated charges and credits

Mid-cycle plan changes generate two line items: a **credit** for the unused portion of your previous plan and a **charge** for the prorated portion of your new plan for the remainder of the cycle. Example: you upgrade from Business to Enterprise on day 18 of a 30-day cycle with 24 seats. You will see:

- `CREDIT - Business plan (12 days remaining, 24 seats)` = `-$X`
- `CHARGE - Enterprise plan (12 days, 24 seats)` = `+$Y`

The net impact on your invoice is `$Y - $X`. If the math looks off, check that the day count matches your plan change date and that the seat count reflects the actual active seat count at the moment of the change, not your contract cap.

## Overage charges

Overage applies when your usage exceeds your plan's included quotas for the billing period. The three most common overage categories:

- **Seat overage** — charged per additional active seat beyond your plan's included count. "Active" is defined as any user who authenticated at least once during the billing period.
- **API call overage** — charged per 1,000 calls beyond the included quota. Rate-limited 429 responses do not count toward overage.
- **Storage overage** — charged per GB-month beyond included storage, prorated to daily granularity.

Overage rates vary by plan and are listed in your order form appendix. If you are seeing unexpected overage, the Usage dashboard (Admin → Billing → Usage) shows a day-by-day breakdown you can reconcile against.

## Credits and adjustments

Credits from support adjustments, SLA breach remedies, or manual goodwill credits appear as negative line items with a reference to the originating ticket or incident. Credits are applied to the current invoice before tax calculation and do not roll over if they exceed the invoice total — contact billing to convert excess credit to a refund.

## Tax

Tax is calculated based on the billing address on file. If your legal entity or registered tax ID has changed, update the billing profile immediately so future invoices reflect the correct tax treatment. Retroactive tax adjustments require a re-issued invoice, which billing can generate on request.

## Related articles

- [kb-0005-seat-provisioning-and-removal.md](kb-0005-seat-provisioning-and-removal.md)
- [kb-0007-data-export-csv-formats.md](kb-0007-data-export-csv-formats.md)
- [kb-0003-api-rate-limits-and-429.md](kb-0003-api-rate-limits-and-429.md)
