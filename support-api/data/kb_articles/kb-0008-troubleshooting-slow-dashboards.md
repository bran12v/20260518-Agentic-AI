# Troubleshooting Slow Dashboards

> **TL;DR:** Dashboard slowness almost always traces to one of four causes: (1) too many saved filters or widgets on a single dashboard, (2) browser cache serving stale JavaScript bundles after a release, (3) network path issues between the user and our CDN, or (4) backend load during peak hours. This article walks through diagnosis in the order you should try.

## Step 1 — Is it just you, or everyone?

Ask two colleagues on different networks and different machines to load the same dashboard. If they see acceptable load times (under 5 seconds for a typical dashboard), the problem is local to your environment — continue to step 2. If they also see slowness, skip ahead to step 4.

## Step 2 — Browser cache and stale bundles

After a release, some users have browsers that cling to the old JavaScript bundle and make extra round-trips trying to reconcile against the new backend. Symptoms: dashboard partially renders, then stalls for 20-60 seconds before finishing.

Fix in order of least to most disruptive:

1. **Hard reload.** Chrome/Edge/Firefox on Windows: `Ctrl+Shift+R`. macOS: `Cmd+Shift+R`. This forces the browser to bypass its cache for the current page.
2. **Open an incognito/private window** and try the same URL. If this is much faster, it confirms a cache issue.
3. **Clear cached files** for the dashboard domain. Keep cookies (clearing them will sign you out).
4. **Disable aggressive extensions** like ad-blockers or privacy extensions on our domain. These can inject delays by inspecting every network request.

If steps 1-4 resolve it, you are done. Otherwise continue.

## Step 3 — Check your saved filter and widget count

The single most common server-side cause of slow dashboards is **filter bloat** — saved filters accumulated over months that each run their own query against our backend.

1. Open the dashboard and count the visible widgets. More than 24 on a single dashboard is a known performance cliff.
2. Open **Dashboard settings → Saved filters**. Check how many saved filters are configured. Over 50 starts to visibly degrade initial load.
3. If either number is high, split the dashboard into multiple dashboards organized by team or task. This is not a workaround — it is the intended usage pattern at scale.

You can also open **Settings → Performance → This dashboard** to see a per-widget load-time breakdown. The slowest 3-5 widgets typically account for 80% of total load time. Remove or simplify those first.

## Step 4 — Network path

If the problem is reproducible across multiple users on the same office network, the issue may be between your office and our CDN.

1. Visit `https://status.support-platform.com` — if we are reporting an incident, you have your answer.
2. Run `curl -o /dev/null -s -w '%{time_total}\n' https://api.support-platform.com/health` from a machine on the affected network. Healthy should return in under 500ms from North America, under 800ms from Europe, under 1200ms from APAC.
3. If `curl` is fast but browser is slow, the issue is browser-specific (step 2 again). If `curl` is slow too, the network path is the problem. Contact your IT team with the timing.

## Step 5 — When to escalate to support

Open a ticket if:

- Multiple users across different networks report slowness simultaneously
- `status.support-platform.com` shows no incident but you are consistently seeing degraded performance
- The Performance panel in Dashboard settings reports that all queries are completing fast but the UI still takes >10 seconds to render

When opening the ticket, include:

- Affected user emails (or at least 3 representative ones)
- Rough start time of the slowness
- Browser + version + OS for at least two affected users
- A screenshot of **Settings → Performance → This dashboard** if available
- A HAR file capture from Chrome DevTools for one slow load (Network tab → right-click → "Save all as HAR with content")

These artifacts cut diagnosis time in half. Without them, support usually has to ask for them and lose a cycle.

## Known performance boundaries

| Factor | Soft limit | Hard cliff |
|--------|-----------|-----------|
| Widgets per dashboard | 24 | 40 |
| Saved filters per user | 50 | 100 |
| Rows per widget query | 10,000 | 50,000 |
| Dashboards auto-opening on sign-in | 3 | 5 |

Staying within the soft limits keeps initial load under 5 seconds on a typical corporate network.

## Related articles

- [kb-0003-api-rate-limits-and-429.md](kb-0003-api-rate-limits-and-429.md)
- [kb-0007-data-export-csv-formats.md](kb-0007-data-export-csv-formats.md)
- [kb-0001-resetting-account-password.md](kb-0001-resetting-account-password.md)
