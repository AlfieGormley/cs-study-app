---
id: rel-multiwindow-alert-detection
title: Multiwindow reset and detection time
level: advanced
minutes: 4
summary: Combine long and short lookbacks and calculate which alert detects a sustained fault first.
sourceLesson: rel-slos-error-budgets
---

The previous unit selected the example workbook thresholds: 14.4 over one hour, 6 over six hours and 1 over three days. Here a short lookback accompanies each long one so old failures stop paging after recovery. Keep those thresholds separate from the instantaneous incident burn rate.

### Adding a short window

A long window alone has a slow *reset*: after you fix the problem, a 1-hour window keeps showing a high error rate for up to an hour, so the alert keeps firing. The fix is to require a **short alert window** (typically 1/12 of the long one) to be burning too:

This executable policy fragment expects `burn_rate` to return the already measured ratio for a named lookback. It has no Prometheus server or scheduler; it simply chooses the most urgent action from the original conditions.

```python
def slo_alert(burn_rate):
  # Both windows must still show bad events.
  fast = (burn_rate("1h") > 14.4
    and burn_rate("5m") > 14.4)
  slow = (burn_rate("6h") > 6
    and burn_rate("30m") > 6)
  ticket = (burn_rate("3d") > 1
    and burn_rate("6h") > 1)
  # The urgent action wins if rules overlap.
  if fast or slow: return "page"
  if ticket: return "ticket"
  return "none"
```

The long window ensures the problem is significant; the short window ensures it's still happening. With both conditions, the 1-hour rule stops firing about five minutes after the errors stop, instead of nearly an hour later.

In Prometheus this is usually built from recording rules for the error ratio over each window (`ratio_rate5m`, `ratio_rate1h` and so on), compared against the corresponding error-ratio threshold:

```formula
e_page = 14.4 × (1 − SLO)
e_page = 14.4 × 0.001 = 0.0144
where
e_page: the error fraction above which the fast page rule is eligible, dimensionless
SLO: the objective as a good-event fraction, here 0.999 (99.9%)
In words: For a 99.9% objective the fast rule requires an error ratio above 0.0144, or 1.44%, in both lookbacks.
```

### Detection time

How fast does a burn-rate alert fire? The workbook gives an approximate detection time for an error rate that starts abruptly, with a clean window beforehand and steady request volume (plus real-world scrape and alert-evaluation delays):

```formula
t_d = ((1 − SLO) / e)wb
where
t_d: detection time in the same units as the long lookback, here minutes, from error onset until the alert fires
SLO: the objective as a fraction, e.g. 0.999
e: the error rate, the fraction of events failing (1 = 100%)
w: the alert's long window, e.g. 60 minutes
b: the alert's burn-rate threshold, e.g. 14.4
In words: the alert fires once the window's average error rate reaches the threshold; a higher error rate gets there sooner.
```

For a full outage (100% errors) against a 99.9% objective, the burn rate is 1,000. The one-hour lookback reaches its 1.44% error threshold after:

```formula
t_d = ((1 − SLO) / e)wb
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

A burn-rate threshold of 14.4 is 72% of the actual burn rate of 20, so the rule needs 72% of the 60-minute lookback filled with these errors: about 43 minutes.

Notice what stays constant: whatever the error rate, the 1-hour rule fires once about 2% of the budget has gone. Big outages page fast, small ones page slowly, but the *cost* at detection is the same. Errors burning below 14.4× are left to the 6-hour rule, and those below 6× to the ticket. Each rule trades detection speed against precision.

## Key takeaways

- A long window establishes significance while its paired short window confirms the problem continues.
- Under clean history and steady traffic, detection follows the time needed for window-average error to reach the threshold.
- Strong failures page fast; lower burn rates need slower rules. Real scrape and evaluation delays add time.

## Further reading

- [Alerting on SLOs (Google SRE workbook)](https://sre.google/workbook/alerting-on-slos/)
