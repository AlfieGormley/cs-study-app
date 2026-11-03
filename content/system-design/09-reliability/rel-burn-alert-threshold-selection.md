---
id: rel-burn-alert-threshold-selection
title: Selecting burn-rate alert thresholds
level: advanced
minutes: 5
summary: Choose meaningful budget spending and reachable error thresholds for alerts.
sourceLesson: rel-slos-error-budgets
---

Burn rate measures bad events against the allowed rate. Here we turn it into an alert threshold: how much budget should disappear, over how long, before a page or ticket is justified? The next unit adds short windows and explains detection time.

## Alerting on SLOs

Naive approaches all have problems:

- **Alert if error rate > SLO threshold (0.1%) over 10 minutes**: fires on short blips that barely touch the budget; very noisy.
- **Alert if error rate over the whole 30 days exceeds budget**: precise, but you'd find out after the budget is already gone.

The SRE workbook's recommendation is **multi-window, multi-burn-rate alerts**. You choose burn rates that correspond to a meaningful fraction of budget consumed in a given lookback window:

Higher burn sustained for longer spends more budget. Under roughly uniform traffic, a 14.4 burn rate over one hour consumes about 2% of a 30-day budget.

For request-based SLIs, the time-ratio calculation assumes roughly uniform request volume. The exact fraction consumed is bad requests in the alert window divided by the full-period request budget; traffic spikes can change it.

For a reference calculation under that assumption: pick the fraction of budget worth waking someone for, and the window over which you want to notice it:

```formula reference
b_alert = fT / w
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

These rows illustrate different urgency levels; choose them for the service rather than treating them as universal defaults.

The burn rates are relative to the budget, so the same thresholds can be reused for other SLOs with the same period; only the error-rate thresholds change. Each threshold must also be reachable: even 100% errors can only burn so fast.

For a 99.9% SLO, the 14.4 burn-rate threshold corresponds to 1.44% errors; total failure burns at 1,000 times the allowed rate. Tightening the SLO lowers the error-rate threshold for the same burn multiplier.

For 99.99% the 14.4× rule fires at 0.144% errors. For a loose SLO such as 90%, the maximum burn rate is just 10, so a 14.4× rule could never fire. The workbook's full example configuration also adds a fourth, ticket-level rule (3× over 24 hours) between the 6-hour and 3-day rules.

## Key takeaways

- Choose a lookback and a meaningful share of budget to spend before alerting.
- The workbook’s example rates are relative to the objective; changing the objective changes the error threshold.
- A rule must be reachable even at total failure. Time fractions approximate request spending only under uniform traffic.

## Further reading

- [Alerting on SLOs (Google SRE workbook)](https://sre.google/workbook/alerting-on-slos/)
