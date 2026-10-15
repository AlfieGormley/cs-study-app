---
id: git-progressive-rollouts
title: Rollout strategies and useful canaries
level: advanced
minutes: 4
sourceLesson: git-cd-release
summary: Rolling versions coexist; blue-green needs spare capacity and compatible state.
---

Continuous delivery produces a tested artefact that can reach production on demand. The next question is how to replace running instances and collect enough evidence before exposing everyone.

## Rollout strategies

| Strategy | How | Rollback |
|---|---|---|
| Recreate | Stop old, start new | Redeploy |
| Rolling | Replace in batches | Roll back batches |
| Blue-green | Switch traffic | Switch back |
| Canary | Small % first | Shift traffic back |

**Recreate** stops old instances before starting new ones and can cause downtime. It can suit any workload whose availability requirements permit that interruption.

**Rolling** replaces instances a few at a time (Kubernetes Deployments do this by default). It needs no spare capacity beyond a small surge, but during the rollout **old and new versions serve traffic simultaneously**, so they must be compatible with each other and with the database.

**Blue-green** runs two full environments. Blue serves traffic; you deploy to green, test it, then switch the router. Rollback is switching back, as long as nothing irreversible (such as a destructive migration) happened. The cost is double capacity during the switch.

**Canary** sends a small share of traffic to the new version and compares it with the old one before expanding:

```
  1%  --10 min-->  check
  5%  --10 min-->  check
 25%  --20 min-->  check
100%
 check: errors, p99 latency, saturation
        canary vs baseline
```

Compare the canary against a **baseline** running the old version at the same scale and time, not against yesterday's numbers; otherwise normal daily variation hides real regressions or triggers misleading alerts.

Is the canary big enough to notice anything? Count how many errors you expect it to see in one stage if nothing is wrong:

```formula
E = R × f × t × e
E = 2000 rps × 0.01 × 600 s × 0.001
E = 20 rps × 600 s × 0.001
E = 12000 × 0.001 = 12
where
E: the number of errors the canary is expected to see in one stage if the new version is exactly as good as the old one
R: the service's total traffic, in requests per second (rps)
f: the canary's share of traffic, as a fraction; 1 % = 0.01
t: the length of the canary stage, in seconds (s); 10 minutes = 600 s
e: the normal error rate, as a fraction of requests; 0.1 % = 0.001
rps: requests per second
s: seconds
In words: canary traffic times stage length gives the number of requests it sees; times the normal error rate gives the errors to expect.
```

> [!example] Is the canary big enough?
> At 2,000 requests per second, a 1% canary sees 20 rps, or 12,000 requests in 10 minutes. If the normal error rate is 0.1%, you expect about 12 errors. A regression that doubles it gives about 24. That is a possible signal, not a guaranteed detection: power depends on the baseline sample, traffic dependence and the chosen test. At 20 rps total, the same canary would see 120 requests and about 0.1 expected errors: it gives little power to detect a modest increase in a rare error rate, though it can reveal a severe regression. Low-traffic services need longer canary stages or synthetic traffic.

## Key takeaways

- Rolling versions coexist; blue-green needs spare capacity and compatible state.
- Canaries compare new and baseline versions before expanding exposure.
- Expected error counts help size a canary but do not guarantee statistical detection.

## Further reading

- [Blue-green deployment — Martin Fowler](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [Canary release — Danilo Sato on martinfowler.com](https://martinfowler.com/bliki/CanaryRelease.html)
- [Canarying releases — Google SRE Workbook](https://sre.google/workbook/canarying-releases/)
