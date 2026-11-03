---
id: rel-correlated-failure-review
title: Reviewing correlated failures
level: basic
minutes: 3
summary: Challenge independence assumptions and audit the complete failure path.
sourceLesson: rel-designing-for-failure
---

The preceding units separated fault symptoms, isolation and survivor capacity. Apply them together before accepting an availability estimate. Adding another copy changes the estimate only when its failure exposure and routing behaviour match the assumptions of the calculation.

## Correlated failure and the "it can't all fail" fallacy

Simple product estimates for redundant copies assume independence.

Independent copies can make simultaneous outages much rarer. That improvement disappears for a fault that hits every copy, such as the same broken migration or shared credentials.

Real failures can correlate:

- The same bad config or software release is applied to both.
- A load spike that kills one replica shifts its load to the other and kills that too (a **cascading failure**).
- Both depend on the same downstream service, DNS or certificate.

Correlation also hides in time. Disks bought in the same batch tend to fail at similar ages, and a RAID rebuild puts heavy load on the surviving disks exactly when you can least afford another failure.

Cascading failures are an important way redundant systems can go fully dark. The rest of this module covers the tools for stopping them: timeouts, retry discipline, circuit breakers, load shedding, and safe deployment.

## A checklist for any design

- List every component and dependency on the request path.
- For each, decide what crash, omission, latency and wrong-answer failures look like.
- Mark SPOFs, including config, DNS, certificates, control planes and humans.
- Decide the fault boundary (host, zone, region, cell) and the blast radius at each.
- Confirm survivors have headroom to absorb a failed peer's load.
- Prefer designs that are statically stable over ones that need a control plane to recover.

## Key takeaways

- Independent replica probabilities do not describe shared bugs, configuration or dependencies.
- A failed replica can overload its survivor and create a cascade.
- Audit component faults, shared dependencies, fault boundaries and survivor headroom together.

## Further reading

- [Static stability using Availability Zones (AWS Builders' Library)](https://aws.amazon.com/builders-library/static-stability-using-availability-zones/)
- [Addressing cascading failures (Google SRE book)](https://sre.google/sre-book/addressing-cascading-failures/)
- [AWS Well-Architected Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
