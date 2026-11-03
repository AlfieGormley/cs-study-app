---
id: rel-canary-evidence-rollout-waves
title: Canary evidence and rollout waves
level: advanced
minutes: 4
summary: Collect comparable evidence before widening exposure across hosts, zones and regions.
sourceLesson: rel-safe-deployments
---

A rolling or blue-green release can expose many users before a rare bug is visible. A canary limits the population first. Expected error counts are evidence-volume estimates; observing ten errors or a difference in counts does not by itself prove statistical significance.

## Canary releases

Send a small fraction of real traffic to the new version, compare its metrics with the old version's, and widen gradually.

```
1%  ──▶ v2   compare errors, latency
5%  ──▶ v2   still good?
25% ──▶ v2
100%──▶ v2
any stage bad → route 0% to v2
```

The key is **comparison**: the canary's error rate and latency are judged against a canary baseline group (the baseline running v1 at the same time, ideally on the same number of hosts), not against a fixed threshold. Tools like Spinnaker's Kayenta and Argo Rollouts run automated canary analysis.

Considerations from the SRE workbook:

- The canary must get enough traffic to be statistically meaningful. 1% of a 100 req/s service is one request a second; a 0.1% error-rate increase would take a long time to detect.
- Bake time must cover slow-to-appear problems: memory leaks, cache expiry, daily batch jobs.
- Canary populations can be hosts, a percentage of requests, or specific users (internal staff first).

A small canary sees few opportunities for a rare regression to appear. At one request per second, an added error probability of 0.1% produces only a few extra errors per hour on average. That is an evidence-volume illustration, not a significance test.

To collect more evidence for small regressions, send the canary more representative traffic or run it longer. Use a simultaneous baseline with comparable workload and per-host load, and choose a suitable statistical test. Matching host counts can reduce workload differences, but reducing the baseline sample does not itself improve statistical precision.

### Staged rollouts at scale

AWS describes deploying in **waves**: first a single box ("one-box"), then one AZ, then one region, then progressively larger groups of regions, with automated monitoring and rollback at each stage and bake time between them. A full global deploy may take days, deliberately. Combined with cell-based architecture, a bad change is usually caught while it affects a tiny fraction of customers.

| Strategy | Extra capacity | Rollback | Exposure |
|---|---|---|---|
| Rolling | spare capacity or surge | batch-dependent | grows by batch |
| Blue-green | ~1× extra (~2× total) | routing-dependent | broad cutover |
| Canary | small | fast | 1% → 100% |

## Automating the guardrails

A mature pipeline does all of this without humans watching graphs:

1. Build once; promote the same artefact through stages.
2. Deploy to one box / canary; run automated analysis against baseline.
3. Bake; check SLO burn rates, errors and latency.
4. Proceed in waves, or **automatically roll back** on regression.
5. Block deploys when the error budget is exhausted (see the SLO lesson) or outside safe hours.

> [!analogy] Real-world analogy: trying a new recipe on a small batch
> A small test batch limits waste, but tasting one piece cannot reveal every problem with ingredients or storage time.
>
> **How it maps:** The batch maps to limited release exposure; representative sampling and waiting map to canary evidence and bake time.
>
> **Where it stops:** Production cohorts can differ, and failures can be correlated or delayed. A successful sample does not prove the whole release safe.

## Key takeaways

- Compare a representative canary against a simultaneous baseline.
- Small canaries observe few errors: more traffic or more time may be needed to detect a small regression.
- Bake through delayed effects and widen in monitored waves with automatic rollback and budget gates.

## Further reading

- [Canarying releases (Google SRE workbook)](https://sre.google/workbook/canarying-releases/)
- [Automating safe, hands-off deployments (AWS Builders' Library)](https://aws.amazon.com/builders-library/automating-safe-hands-off-deployments/)
- [Canary release (Martin Fowler)](https://martinfowler.com/bliki/CanaryRelease.html)
- [Release engineering (Google SRE book)](https://sre.google/sre-book/release-engineering/)
