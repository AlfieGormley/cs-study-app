---
id: git-progressive-rollouts
title: Rollout strategies and useful canaries
level: advanced
minutes: 5
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

> [!analogy] Real-world analogy: trialling a new dish on a few tables
> A restaurant tries a new recipe on a handful of tables on a Friday evening. To judge it fairly, it compares those diners with tables served the old recipe on the same evening, not with last Tuesday's quieter crowd. If the trial tables send plates back, the kitchen stops serving the new recipe before the whole room gets it.
>
> **How it maps:** The trial tables are the canary, the same-evening tables on the old recipe are the baseline, and sending plates back is a rise in errors or latency. Stopping early is rolling back before full exposure.
>
> **Where it stops:** A handful of diners gives a noisy verdict; a canary's evidence also depends on how much traffic it sees, and a few extra errors can be chance. Unlike a dish, a bad release can also harm shared systems such as a database used by both versions.

Is the canary big enough to notice anything? Estimate how many errors it should see in one stage if nothing is wrong: its share of the traffic, times the stage length, times the normal error rate.

```formula reference
E = R × f × t × e
where
E: the number of errors the canary is expected to see in one stage if the new version is exactly as good as the old one
R: the service's total traffic, in requests per second (rps)
f: the canary's share of traffic, as a fraction; 1 % = 0.01
t: the length of the canary stage, in seconds (s)
e: the normal error rate, as a fraction of requests; 0.1 % = 0.001
rps: requests per second
In words: canary traffic times stage length gives the number of requests it sees; times the normal error rate gives the errors to expect.
```

> [!example] Is the canary big enough?
> At 2,000 requests per second, a 1% canary sees 20 rps, or 12,000 requests in 10 minutes. If the normal error rate is 0.1%, you expect about 12 errors. A regression that doubles it gives about 24. That is a possible signal, not a guaranteed detection: power depends on the baseline sample, traffic dependence and the chosen test. At 20 rps total, the same canary would see 120 requests and about 0.1 expected errors: it gives little power to detect a modest increase in a rare error rate, though it can reveal a severe regression. Low-traffic services need longer canary stages or synthetic traffic.

When the expected count is only a handful, a few extra errors can easily be chance. The signal to roll back is a clear, sustained gap between canary and baseline on errors, latency or saturation, over enough requests that chance is an unlikely explanation.

## Key takeaways

- Rolling versions coexist; blue-green needs spare capacity and compatible state.
- Canaries compare new and baseline versions before expanding exposure.
- Expected error counts help size a canary but do not guarantee statistical detection.

## Further reading

- [Blue-green deployment — Martin Fowler](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [Canary release — Danilo Sato on martinfowler.com](https://martinfowler.com/bliki/CanaryRelease.html)
- [Canarying releases — Google SRE Workbook](https://sre.google/workbook/canarying-releases/)
