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
| Error budget | the failure the SLO allows | 0.1% may fail |

- **SLI (service level indicator)**: a carefully defined quantitative measure of some aspect of service, ideally a ratio of good events to total events.
- **SLO (service level objective)**: the target value for the SLI over a window.
- **SLA (service level agreement)**: a business contract stating consequences (refunds, credits) if a level is missed. SLAs should be *looser* than internal SLOs, so you notice and react long before you owe customers money.

## Choosing good SLIs

The SRE workbook recommends expressing every SLI as:

```formula
SLI = G / V × 100%
SLI = 999,000 / 1,000,000 × 100%
SLI = 99.9%
where
SLI: the service level indicator, as a percentage from 0 to 100%
G: good events, e.g. requests that succeeded within the latency threshold, here 999,000
V: valid events, all events that count (excluding things like health checks), here 1,000,000
%: per cent
In words: the SLI is the share of valid events that were good. 999,000 good requests out of a million valid ones is an SLI of 99.9%.
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

Pick an SLO from what users need and what you can achieve, not from aspiration. Start from historical performance, then tighten if users are unhappy. Remember the maths of hard dependencies in series: a hard, synchronous dependency with 99.9% achieved availability caps its caller under the same measurement and failure conditions unless retries, caching or another recovery mechanism masks its failures. A dependency's contractual target alone is not a measured ceiling.

## Error budgets

If the SLO is 99.9%, the **error budget** is the remaining 0.1%. It's an allowance of failure for the window, and you can count it in requests or in time:

```formula
B = 1 − SLO
B = 1 − 0.999 = 0.001 = 0.1%
B_req = B × N
B_req = 0.001 × 100,000,000 = 100,000
B_time = B × T
B_time = 0.001 × 40,320 min ≈ 40 min
where
B: the error budget as a fraction of events (or of time)
SLO: the service level objective as a fraction, here 99.9% = 0.999
B_req: the number of failed requests allowed in the window
N: the valid requests in the window, here 100 million in 28 days
B_time: the full-outage time allowed in the window
T: the window length, 28 days = 40,320 minutes (min)
min: minutes
≈: approximately equal to (rounded)
%: per cent
In words: a 99.9% SLO lets 1 in 1,000 events fail: 100,000 of 100 million requests, or about 40 minutes of total outage in 28 days.
```

The time view assumes traffic is spread evenly; an outage at peak spends more of a request-based budget than the same outage at night.

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

```formula
b = e / (1 − SLO)
b = 1.44% / (1 − 99.9%)
b = 1.44% / 0.1% = 14.4
where
b: the burn rate, a plain multiplier with no unit (1 = burning exactly on budget)
e: the observed error rate, the fraction of valid events that are bad, here 1.44%
SLO: the service level objective, here 99.9%
1 − SLO: the error budget as a rate, here 0.1%
%: per cent
In words: errors at 1.44% against a 0.1% budget burn the budget 14.4 times faster than the rate that would just use it up by the end of the window.
```

For the following exhaustion-time examples, assume steady traffic, a full initial budget and no additional old errors aging out. The time until the budget is gone is the window divided by the burn rate:

```formula
t_out = T / b
t_out = 30 days / 14.4
t_out = 720 h / 14.4 = 50 h
where
t_out: the time until the whole error budget is spent
T: the SLO window, here 30 days = 720 hours (h)
b: the burn rate, here 14.4
days: calendar days; 1 day = 24 h
h: hours
In words: at burn rate 14.4 a 30-day budget lasts only 50 hours.
```

- Burn rate 1: you'll use exactly 100% of the budget by the end of the window.
- Burn rate 2: budget gone in half the window.
- Burn rate 14.4 with a 30-day window: budget gone in about 50 hours.

## Alerting on SLOs

Naive approaches all have problems:

- **Alert if error rate > SLO threshold (0.1%) over 10 minutes**: fires on short blips that barely touch the budget; very noisy.
- **Alert if error rate over the whole 30 days exceeds budget**: precise, but you'd find out after the budget is already gone.

The SRE workbook's recommendation is **multi-window, multi-burn-rate alerts**. You choose burn rates that correspond to a meaningful fraction of budget consumed in a given lookback window:

```formula
f = b × w / T
f = 14.4 × 1 h / 720 h = 0.02 = 2%
where
f: the fraction of the whole period's error budget consumed
b: the burn rate during the alert window, here 14.4
w: the alert's lookback window, here 1 hour (h)
T: the SLO period, here 30 days = 720 h
h: hours
%: per cent
In words: burning at 14.4 times the sustainable rate for one hour spends 2% of a 30-day budget.
```

For request-based SLIs, the time-ratio calculation assumes roughly uniform request volume. The exact fraction consumed is bad requests in the alert window divided by the full-period request budget; traffic spikes can change it.

Rearranged under that assumption, it tells you which burn rate to alert on: pick the fraction of budget worth waking someone for, and the window over which you want to notice it:

```formula
b_alert = f × T / w
b_alert = 0.02 × 720 h / 1 h = 14.4
where
b_alert: the burn rate at which the alert should fire
f: the fraction of budget worth alerting on, here 2% = 0.02
T: the SLO period, here 720 hours (h)
w: the lookback window, here 1 h
h: hours
In words: to page when 2% of a 30-day budget has gone within one hour, alert at a burn rate of 14.4.
```

The workbook's recommended starting point for a 99.9% SLO over 30 days (720 hours):

| Burn rate | Long window | Budget used | Action |
|---|---|---|---|
| 14.4 | 1 hour | 2% | page |
| 6 | 6 hours | 5% | page |
| 1 | 3 days | 10% | ticket |

Check each row with the budget-consumed formula:

```formula
f = b × w / T
f = 14.4 × 1 h / 720 h = 2%
f = 6 × 6 h / 720 h = 5%
f = 1 × 72 h / 720 h = 10%
where
f: the fraction of the 30-day error budget used when the alert fires
b: the burn-rate threshold of the rule
w: the rule's long window: 1 h, 6 h or 3 days = 72 h
T: the SLO period, 30 days = 720 hours (h)
h: hours
%: per cent
In words: the three rules fire after 2%, 5% and 10% of the monthly budget has gone.
```

The burn rates are relative to the budget, so the same thresholds can be reused for other SLOs with the same period; only the error-rate thresholds change. Each threshold must also be reachable: even 100% errors can only burn so fast.

```formula
e_alert = b × (1 − SLO)
e_alert = 14.4 × 0.1% = 1.44%
b_max = 1 / (1 − SLO)
b_max = 1 / 0.001 = 1,000
where
e_alert: the error rate at which a burn-rate rule fires
b: the rule's burn-rate threshold, here 14.4
SLO: the objective, here 99.9%, so 1 − SLO = 0.1% = 0.001
b_max: the highest burn rate possible, reached when every event fails
%: per cent
In words: for a 99.9% SLO the 14.4× rule fires at 1.44% errors, and a total outage burns at 1,000×. For a 99% SLO, b_max is only 100.
```

For 99.99% the 14.4× rule fires at 0.144% errors. For a loose SLO such as 90%, the maximum burn rate is just 10, so a 14.4× rule could never fire. The workbook's full example configuration also adds a fourth, ticket-level rule (3× over 24 hours) between the 6-hour and 3-day rules.

### Adding a short window

A long window alone has a slow *reset*: after you fix the problem, a 1-hour window keeps showing a high error rate for up to an hour, so the alert keeps firing. The fix is to require a **short alert window** (typically 1/12 of the long one) to be burning too:

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

```formula
t_d = (1 − SLO) / e × w × b
where
t_d: the detection time, from when errors start until the alert fires
SLO: the objective as a fraction, e.g. 0.999
e: the error rate, the fraction of events failing (1 = 100%)
w: the alert's long window, e.g. 60 minutes
b: the alert's burn-rate threshold, e.g. 14.4
In words: the alert fires once the window's average error rate reaches the threshold; a higher error rate gets there sooner.
```

For a full outage (100% errors) against a 99.9% SLO, the burn rate is 1 / 0.001 = 1,000. The 1-hour window's average error rate passes 1.44% (14.4 × 0.1%) after:

```formula
t_d = (1 − SLO) / e × w × b
t_d = 0.001 / 1 × 60 min × 14.4
t_d ≈ 0.86 min ≈ 52 s
t_d = 0.001 / 0.02 × 60 min × 14.4
t_d ≈ 43 min
where
t_d: the detection time
SLO: here 99.9% = 0.999, so 1 − SLO = 0.001
e: the error rate: 1 (100%, a full outage) in the first case, 0.02 (2%) in the second
w: the long window, 60 minutes (min)
b: the rule's burn-rate threshold, 14.4
min: minutes
s: seconds
≈: approximately equal to (rounded)
In words: a total outage pages in under a minute; a 2% error rate (burn rate 20) takes about 43 minutes to page on the 1-hour rule.
```

The 43 minutes is the same as 14.4 / 20 of the 60-minute window: the rule waits until the window's average error rate catches up with the threshold.

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
- Express SLIs as the share of valid events that were good, measured as close to the user as practical, for critical user journeys.
- The error budget is the failure the SLO allows (0.1% for 99.9%). A pre-agreed policy turns it into release decisions.
- Burn rate is the error rate divided by the error budget. Under uniform request volume, the budget consumed is the burn rate times the alert window as a fraction of the period; otherwise use actual event counts.
- Use multi-window, multi-burn-rate alerts (e.g. 14.4× over 1h and 5m) to page quickly on real problems and stop paging once they're fixed.

## Further reading

- [Service level objectives (Google SRE book)](https://sre.google/sre-book/service-level-objectives/)
- [Alerting on SLOs (Google SRE workbook)](https://sre.google/workbook/alerting-on-slos/)
- [Implementing SLOs (Google SRE workbook)](https://sre.google/workbook/implementing-slos/)
- [Error budget policy (Google SRE workbook)](https://sre.google/workbook/error-budget-policy/)
- [Embracing risk (Google SRE book)](https://sre.google/sre-book/embracing-risk/)
