---
id: rel-error-budget-policy-burn
title: Error budgets, policy and burn rate
level: advanced
minutes: 4
summary: Convert an objective into allowed bad events and a release policy.
sourceLesson: rel-slos-error-budgets
---

Good and valid events from the SLI unit define the accounting boundary. This unit assumes that boundary remains consistent. Distinguish request budgets from outage minutes: a peak-time outage can spend a request budget much faster.

## Error budgets

If the SLO is 99.9%, the **error budget** is the remaining 0.1%. It's an allowance of failure for the window, and you can count it in requests or in time:

```formula
B = 1 − SLO
B = 1 − 0.999 = 0.001 = 0.1%
B_req = BN
B_req = 0.001 × 100,000,000 = 100,000
B_time = BT
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

## Key takeaways

- The error budget is the share of valid events the objective allows to be bad.
- Agree the policy before incidents: examples freeze ordinary releases when the trailing budget is exhausted.
- Burn rate divides observed bad-event rate by allowed rate. Time-based spending estimates require steady request volume.

## Further reading

- [Service level objectives (Google SRE book)](https://sre.google/sre-book/service-level-objectives/)
- [Error budget policy (Google SRE workbook)](https://sre.google/workbook/error-budget-policy/)
- [Embracing risk (Google SRE book)](https://sre.google/sre-book/embracing-risk/)
