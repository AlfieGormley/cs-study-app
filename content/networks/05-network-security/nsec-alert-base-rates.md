---
id: nsec-alert-base-rates
title: Why a rare attack creates many false alerts
level: advanced
minutes: 4
summary: Alert precision depends on attack prevalence as well as detector sensitivity.
sourceLesson: nsec-detection
---

A detector with a small false-positive rate can still create a large investigation workload. The denominator matters: rare malicious events may be outnumbered by benign events by many orders of magnitude.

### The base-rate problem

Even a small false-positive rate can overwhelm true alerts when malicious events are rare. The question an analyst cares about is: when an alert fires, how likely is it to be real? That fraction is the detector's **alert precision**. It depends on how common attacks are (the **base rate**) as well as on the detector, because the false alerts come from the huge pool of benign events while the true alerts come from the tiny pool of malicious ones.

Consider a network that sees 10,000,000 connections a day, of which 100 are malicious. A detector catches 99 % of attacks and wrongly flags only 0.1 % of benign connections. On a typical day you would expect:

| Alerts | Expected per day |
|---|---|
| Real attacks caught (99 % of 100) | about 99 |
| Benign connections flagged (0.1 % of 9,999,900) | about 10,000 |
| Share of alerts that are real | about 1 % |

So roughly 99 of every 100 alerts are false, even though the detector sounds excellent on paper. Nothing is broken: benign connections outnumber attacks 100,000 to one, so a tiny false-positive rate still produces far more false alerts than there are attacks to find. That workload can make triage difficult; it does not prove that every analyst will miss the true alerts.

The same reasoning predicts which changes help. Catching 100 % of attacks instead of 99 % adds about one real alert and leaves precision near 1 %. Cutting the false-positive rate tenfold, to 0.01 %, leaves about 1,000 false alerts and lifts precision to about 9 %. A higher base rate would also raise precision, which is why the same rule can be useful on a small, high-risk network segment and useless across a whole network.

```formula reference
precision = tp / (tp + (1 − p)f)
where
precision: the fraction of alerts that are real attacks, from 0 to 1 (also called positive predictive value)
p: prevalence (the base rate): the fraction of all events that are malicious
t: sensitivity (true-positive rate): the fraction of malicious events the detector flags
f: false-positive rate: the fraction of benign events the detector wrongly flags
In words: real alerts are the detected share of the rare malicious events; false alerts are the wrongly flagged share of the much larger number of benign events; precision is real alerts divided by all alerts, so when attacks are rare the false-positive rate dominates.
```

This is Bayes' theorem applied to alerts. The counts above are expected values under constant rates, not guaranteed daily outcomes, and precision is undefined if the detector never alerts.

> [!analogy] Real-world analogy: screening everyone for a rare illness
> A clinic screens 10,000 healthy-looking people for an illness that only one of them has. Even a test that is wrong for just 1 in 1,000 healthy people will flag about ten of them, so a positive result is far more likely to be a false alarm than a real case.
>
> **How it maps:** The people screened are network connections, the illness is an attack, the test's false-alarm rate on healthy people is the detector's false-positive rate, and the chance that a positive result is real is alert precision. Screening a high-risk group instead, where the illness is common, is like applying a rule only where attacks are likely.
>
> **Where it stops:** Patients do not change their symptoms to fool the test, but attackers deliberately make malicious traffic look benign, and network traffic is not a set of independent cases with fixed rates. Real rates must be measured in your own environment.

This is why mature teams tune aggressively, suppress noisy rules, correlate network alerts with host and identity signals in a SIEM, and measure precision in their own environment. Malware-domain and honeypot alerts can be useful, but shared infrastructure, research traffic and mistakes can still create false positives.

## Key takeaways
- Alert precision depends on attack prevalence as well as detector sensitivity.
- Cutting false positives raises precision far more than catching the last few attacks.
- The worked counts are expected values, not guaranteed daily outcomes.
- Tune and correlate evidence using the actual operating environment.

## Further reading
- [Base rate fallacy — Wikipedia](https://en.wikipedia.org/wiki/Base_rate_fallacy)
- [Positive and negative predictive values — Wikipedia](https://en.wikipedia.org/wiki/Positive_and_negative_predictive_values)
