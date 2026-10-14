---
id: fund-recovery-mttr
title: Improve availability by shortening recovery
level: intermediate
minutes: 3
summary: Use MTBF and MTTR to identify investments in detection, diagnosis, failover and verification.
sourceLesson: fund-availability
---

Redundancy is only part of resilience. When service does fail, reducing the time users wait for recovery can be a more practical investment than trying to eliminate every failure.

## MTBF and MTTR

Two quantities define steady-state availability:

- **MTBF** (mean time between failures): how long, on average, the system runs before failing.
- **MTTR** (mean time to repair/recovery): how long, on average, it takes to restore service.

Over a long run, the system cycles between working (for MTBF on average) and being repaired (for MTTR on average). The fraction of each cycle spent working is the availability:

```formula
A = MTBF / (MTBF + MTTR)
A = 1,000 h / (1,000 h + 1 h) ≈ 0.999
where
A: the steady-state availability, the long-run fraction of time the system is up
MTBF: mean time between failures, the average time it runs before failing, here in hours (h)
MTTR: mean time to repair (or recovery), the average time to restore service after a failure, in the same unit as MTBF
h: hour
≈: approximately equal to (rounded)
In words: availability is the up-time of a typical cycle divided by the whole cycle, up-time plus repair time.
```

Example: a server fails on average every 1,000 hours and takes 1 hour to fix, which gives 1,000 / 1,001 ≈ 99.9%. The formula assumes failures and repairs keep repeating at these average rates; it says nothing about how bad any single outage is.

There are two levers:

1. **Increase MTBF**: better hardware, fewer risky changes, more testing.
2. **Decrease MTTR**: faster detection, automated failover, quick rollbacks, good runbooks.

Lowering MTTR is often cheaper and more effective. Cutting MTTR from 60 minutes to 6 gives the same availability gain as making failures 10x rarer. Recovery time itself breaks down into:

```formula
MTTR = t_detect + t_diagnose
     + t_fix + t_verify
where
MTTR: mean time to repair (or recovery), the average time from failure to restored service; express every stage in the same unit, such as minutes
t_detect: the time until anyone (or any alert) notices the failure
t_diagnose: the time to work out what is wrong
t_fix: the time to fix it, fail over to a standby or roll back
t_verify: the time to confirm service is really restored
In words: recovery time is the sum of noticing, understanding, fixing and checking, so shortening any stage shortens recovery.
```

Each piece suggests an investment: alerting on symptoms (detect), good dashboards and tracing (diagnose), automated failover and one-click rollback (fix).

Related terms you'll see: **MTTF** (mean time *to* failure, for non-repairable parts) and **MTTD** (mean time to detect).

## Key takeaways
- Long-run availability depends on time working relative to time working plus recovery time.
- Making recovery ten times faster has the same modelled availability effect as making failures ten times rarer.
- Separate detection, diagnosis, repair and verification to choose concrete recovery improvements.

## Further reading
- [Availability and Beyond (AWS)](https://docs.aws.amazon.com/whitepapers/latest/availability-and-beyond-improving-resilience/availability-and-beyond-improving-resilience.html)
- [Embracing Risk (Google SRE)](https://sre.google/sre-book/embracing-risk/)
