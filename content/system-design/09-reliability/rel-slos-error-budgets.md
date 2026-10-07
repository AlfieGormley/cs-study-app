---
id: rel-slos-error-budgets
title: SLIs, SLOs, SLAs and error budgets
level: advanced
minutes: 15
summary: Choose SLIs that reflect user experience, set SLOs, turn them into error budgets, and alert with multi-window burn rates the way Google SRE does.
---

"Make it as reliable as possible" is not a target. Higher reliability targets generally require investment. Choose them from user needs and measured end-to-end behavior; the benefit depends on the workload and its other failure modes.

Google's SRE approach replaces vague goals with three precise concepts, and turns the gap between perfect and good enough into a budget teams can spend.

The fundamentals module covered what the nines mean in downtime per year. Here we use those numbers operationally.

## The vocabulary

| Term | What it is | Example |
|---|---|---|
| SLI | a measurement | % of requests < 300ms |
| SLO | a target for an SLI | 99.9% over 28 days |
| SLA | a contract with penalties | 99.5% or credits |
| Error budget | 1 − SLO | 0.1% may fail |

- **SLI (service level indicator)**: a carefully defined quantitative measure of some aspect of service, ideally a ratio of good events to total events.
- **SLO (service level objective)**: the target value for the SLI over a window.
- **SLA (service level agreement)**: a business contract stating consequences (refunds, credits) if a level is missed. SLAs should be *looser* than internal SLOs, so you notice and react long before you owe customers money.

## Choosing good SLIs

The SRE workbook recommends expressing every SLI as:

```
SLI = good events / valid events × 100%
```

This gives a number between 0 and 100% that's easy to reason about and aggregate.

Common SLI types by kind of system:

| System | SLI types |
|---|---|
| Request/response API | availability, latency, quality |
| Data pipeline | freshness, correctness, coverage |
| Storage | durability, latency |

### Make SLIs reflect what users feel

- **Measure as close to the user as practical.** Server logs miss requests that never arrived (DNS, load balancer, TLS failures). Load balancer logs are better; client-side measurements or synthetic probes are closer still, but noisier.
- **Define "good" precisely.** "Availability" might be "HTTP status not 5xx", but a `200` with an empty search result due to a backend timeout is also bad. Latency SLIs need thresholds, e.g. "served in under 300 ms".
- **Use percentile thresholds via ratios.** "99% of requests faster than 300 ms" is a ratio SLI, so it can have an error budget. "p99 < 300 ms" is harder to budget.
- **Focus on critical user journeys.** For a shop: search, view product, add to basket, checkout. A slow "update avatar" endpoint matters less than a failing checkout.
- **Exclude invalid events**, such as health checks or requests rejected for bad input (4xx caused by the client).

> [!example] A concrete SLI spec
> "Proportion of `POST /checkout` requests, measured at the load balancer, that return a non-5xx status in under 800 ms, excluding synthetic health checks." SLO: 99.9% over a rolling 28 days.

### How many nines?

Pick an SLO from what users need and what you can achieve, not from aspiration. Start from historical performance, then tighten if users are unhappy. Remember the serial dependency maths: a hard, synchronous dependency with 99.9% achieved availability caps its caller under the same measurement and failure conditions unless retries, caching or another recovery mechanism masks its failures. A dependency's contractual target alone is not a measured ceiling.

## Error budgets

If the SLO is 99.9%, the **error budget** is the remaining 0.1%. It's an allowance of failure for the window.

```
Requests in 28 days:  100,000,000
SLO:                  99.9%
Error budget:         0.1% = 100,000
                      failed requests
```

For a time-based view, 0.1% of 28 days is about 40 minutes of full outage.

### Error budget policy

The budget becomes useful when it drives decisions. Google's example policy:

- **Budget remaining**: ship features freely; take risks (experiments, faster rollouts).
- **Budget exhausted** over the trailing four weeks: halt changes and releases other than urgent fixes and security patches until the service is back within SLO.
- **Single incident consumes > 20% of the four-week budget**: mandatory postmortem with at least one top-priority action item.

With a rolling window, old events leave as new ones arrive. Remaining budget may rise or fall depending on their good/bad mix and request volume; it does not reset on the first of the month.

This aligns product and SRE incentives. Product teams want to ship; SRE wants stability. The budget is an objective, pre-agreed way to decide between them, rather than an argument during each release.

> [!tip] 100% is the wrong target
> If you're consistently using none of your error budget, your SLO may be too loose or you're over-investing in reliability. Spending budget on faster releases or planned maintenance is the point of having one.

## Burn rate

**Burn rate** is how fast you're consuming the error budget relative to the rate that would exactly exhaust it at the end of the window.

```
burn rate = observed error rate
            ÷ (1 − SLO)
```

For the following exhaustion-time examples, assume steady traffic, a full initial budget and no additional old errors aging out.

- Burn rate 1: you'll use exactly 100% of the budget by the end of the window.
- Burn rate 2: budget gone in half the window.
- Burn rate 14.4 with a 30-day window: budget gone in `30 days / 14.4 ≈ 50 hours`.

For a 99.9% SLO (budget 0.1%), an error rate of 1.44% is burn rate 14.4.

## Alerting on SLOs

Naive approaches all have problems:

- **Alert if error rate > SLO threshold (0.1%) over 10 minutes**: fires on short blips that barely touch the budget; very noisy.
- **Alert if error rate over the whole 30 days exceeds budget**: precise, but you'd find out after the budget is already gone.

The SRE workbook's recommendation is **multi-window, multi-burn-rate alerts**. You choose burn rates that correspond to a meaningful fraction of budget consumed in a given lookback window:

```
budget consumed =
  burn rate × window / SLO period
```

For request-based SLIs, the time-ratio calculation assumes roughly uniform request volume. The exact fraction consumed is bad requests in the alert window divided by the full-period request budget; traffic spikes can change it.

Rearranged under that assumption, it tells you which burn rate to alert on: pick the fraction of budget worth waking someone for, and the window over which you want to notice it:

```
burn rate threshold =
  budget fraction × period / window
```

The workbook's recommended starting point for a 99.9% SLO over 30 days (720 hours):

| Burn rate | Long window | Budget used | Action |
|---|---|---|---|
| 14.4 | 1 hour | 2% | page |
| 6 | 6 hours | 5% | page |
| 1 | 3 days | 10% | ticket |

Check: `14.4 × 1h / 720h = 2%`. `6 × 6h / 720h = 5%`. `1 × 72h / 720h = 10%`.

The burn rates are relative to the budget, so the same thresholds can be reused for other SLOs with the same period; check that each threshold is attainable (maximum burn is `1 / (1 − SLO)`), especially for looser SLOs. only the error-rate thresholds change. For 99.9% the 14.4× rule fires at `14.4 × 0.1% = 1.44%` errors; for 99.99% it fires at 0.144%. The workbook's full example configuration also adds a fourth, ticket-level rule (3× over 24 hours) between the 6-hour and 3-day rules.

### Adding a short window

A long window alone has a slow *reset*: after you fix the problem, a 1-hour window keeps showing a high error rate for up to an hour, so the alert keeps firing. The fix is to require a **short window** (typically 1/12 of the long one) to be burning too:

```
page if:
  burn_rate(1h)  > 14.4 AND
  burn_rate(5m)  > 14.4
OR
  burn_rate(6h)  > 6 AND
  burn_rate(30m) > 6
ticket if:
  burn_rate(3d)  > 1 AND
  burn_rate(6h)  > 1
```

The long window ensures the problem is significant; the short window ensures it's still happening. With both conditions, the 1-hour rule stops firing about five minutes after the errors stop, instead of nearly an hour later.

In Prometheus this is usually built from recording rules for the error ratio over each window (`ratio_rate5m`, `ratio_rate1h` and so on), compared against `14.4 * 0.001` and similar constants.

### Detection time

How fast does a burn-rate alert fire? The workbook gives an approximate detection time for an error rate that starts abruptly, with a clean window beforehand and steady request volume (plus real-world scrape and alert-evaluation delays):

```
detection time =
  (1 − SLO) / error rate
  × window × burn rate
```

For a full outage (100% errors) against a 99.9% SLO, the burn rate is `1 / 0.001 = 1000`. The 1-hour window's average error rate exceeds `14.4 × 0.1% = 1.44%` after:

```
0.001 / 1 × 60 min × 14.4
  ≈ 0.86 min ≈ 52 s
```

So a total outage pages in under a minute, while a 2% error rate (burn rate 20) takes `14.4/20 × 60 ≈ 43 minutes` to page on the 1-hour rule.

Notice what stays constant: whatever the error rate, the 1-hour rule fires once about 2% of the budget has gone. Big outages page fast, small ones page slowly, but the *cost* at detection is the same. Errors burning below 14.4× are left to the 6-hour rule, and those below 6× to the ticket. Each rule trades detection speed against precision.

### Low-traffic services

With 10 requests in an hour, one failure gives a 10% hourly error rate and can trigger the fast page rule; longer windows depend on their own event counts. The workbook's options:

- **Generate representative synthetic traffic** to detect persistent failures; keep real-user outcomes visible so synthetic successes do not hide user-specific problems.
- **Aggregate small services** that share failure modes into one combined SLO.
- **Change the product** so a single failure matters less (client-side retries, for example).
- **Lower the SLO or lengthen the windows**, accepting slower detection where a brief failure has little real impact.

## Putting it to work

1. Pick 2–4 critical user journeys.
2. Define a ratio SLI for each, measured near the user.
3. Set SLOs from historical data and user expectations.
4. Agree an error-budget policy with product leadership *before* it's needed.
5. Implement multi-window burn-rate alerts; delete cause-based pages that no longer add value.
6. Review SLOs quarterly.

## Key takeaways

- SLIs measure, SLOs set targets, SLAs are contracts; keep SLAs looser than SLOs.
- Express SLIs as good events / valid events, measured as close to the user as practical, for critical user journeys.
- Error budget = 1 − SLO. A pre-agreed policy turns it into release decisions.
- Burn rate = error rate / (1 − SLO). Under uniform request volume, budget consumed = burn rate × window / period; otherwise use actual event counts.
- Use multi-window, multi-burn-rate alerts (e.g. 14.4× over 1h and 5m) to page quickly on real problems and stop paging once they're fixed.

## Further reading

- [Service level objectives (Google SRE book)](https://sre.google/sre-book/service-level-objectives/)
- [Alerting on SLOs (Google SRE workbook)](https://sre.google/workbook/alerting-on-slos/)
- [Implementing SLOs (Google SRE workbook)](https://sre.google/workbook/implementing-slos/)
- [Error budget policy (Google SRE workbook)](https://sre.google/workbook/error-budget-policy/)
- [Embracing risk (Google SRE book)](https://sre.google/sre-book/embracing-risk/)
