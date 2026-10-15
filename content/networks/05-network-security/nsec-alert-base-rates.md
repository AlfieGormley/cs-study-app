---
id: nsec-alert-base-rates
title: Why a rare attack creates many false alerts
level: advanced
minutes: 3
summary: Alert precision depends on attack prevalence as well as detector sensitivity.
sourceLesson: nsec-detection
---

A detector with a small false-positive rate can still create a large investigation workload. The denominator matters: rare malicious events may be outnumbered by benign events by many orders of magnitude.

### The base-rate problem

Even a small false-positive rate can overwhelm true alerts when malicious events are rare. The question an analyst cares about is: when an alert fires, how likely is it to be real? That fraction is the detector's **alert precision**, and it depends on how common attacks are (the base rate) as well as on the detector:

```formula
precision = tp / (tp + f(1 − p))
where
precision: the fraction of alerts that are real attacks, from 0 to 1 (also called positive predictive value)
p: prevalence (the base rate): the fraction of all events that are malicious
t: sensitivity (true-positive rate): the fraction of malicious events the detector flags
f: false-positive rate: the fraction of benign events the detector wrongly flags
In words: real alerts are the detected share of the rare bad events; false alerts are the wrongly flagged share of the huge number of good events; precision is real alerts divided by all alerts.
```

This is Bayes' theorem applied to alerts. It assumes the rates are constant across events, and it is undefined if the detector never alerts (the bottom line is zero).

**Working it out.** A network sees 10,000,000 connections a day, of which 100 are malicious. A detector catches 99 % of attacks and flags only 0.1 % of benign connections:

```formula
A_true = N_bad t = 100 × 0.99 = 99
A_false = N_good f
A_false = 9999900 × 0.001 ≈ 10000
precision = A_true / (A_true + A_false)
precision = 99 / (99 + 10000) ≈ 0.01
where
A_true: expected alerts on malicious connections per day
A_false: expected alerts on benign connections per day
N_bad: malicious connections per day, here 100
N_good: benign connections per day, here 10,000,000 − 100 = 9,999,900
t: sensitivity, here 0.99 (99 %)
f: false-positive rate, here 0.001 (0.1 %)
precision: the fraction of alerts that are real
≈: approximately equal to (rounded)
In words: about 99 real alerts are buried among about 10,000 false ones, so only about 1 % of alerts are real.
```

About 99 % of alerts are false in this model. That workload can make triage difficult; it does not prove that every analyst will miss the true alerts.

This is why mature teams tune aggressively, suppress noisy rules, correlate network alerts with host and identity signals in a SIEM, and measure precision in their own environment. Malware-domain and honeypot alerts can be useful, but shared infrastructure, research traffic and mistakes can still create false positives.

## Key takeaways
- Alert precision depends on attack prevalence as well as detector sensitivity.
- The worked counts are expected values, not guaranteed daily outcomes.
- Tune and correlate evidence using the actual operating environment.

## Further reading
- [Suricata rules format — Suricata docs](https://docs.suricata.io/en/latest/rules/intro.html)
- [tcpdump and libpcap](https://www.tcpdump.org/)
- [Wireshark display filters — Wireshark wiki](https://wiki.wireshark.org/DisplayFilters)
- [Logging IP traffic using VPC Flow Logs — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html)
- [RFC 7011: IPFIX Protocol Specification](https://www.rfc-editor.org/rfc/rfc7011)
- [Zeek documentation](https://docs.zeek.org/en/v7.1.1/logs/index.html)
- [Base rate fallacy — Wikipedia](https://en.wikipedia.org/wiki/Base_rate_fallacy)
