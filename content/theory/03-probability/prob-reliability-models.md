---
id: prob-reliability-models
title: Model series and redundant availability
level: basic
minutes: 3
sourceLesson: prob-basics
summary: Series systems require every component to work.
---

Availability asks whether a service is working at a sampled instant, or what fraction of time it is serving. The first modelling decision is which components must be working together.

## Required dependencies versus alternatives

In a **series system**, every required component must work. A checkout path needing a gateway, authentication and payment service fails when any required link fails. Adding another required dependency cannot improve availability in this model. With independent component states, multiply their availabilities. When at least two required components each have availability strictly between zero and one, the path is less available than either one alone.

In **parallel redundancy**, any one replica is sufficient. With perfect routing and failover and no other failure causes, the service fails only when all replicas are down. Under mutual independence, multiply the downtime probabilities and take the complement. This can produce a large improvement, but the assumptions do the work.

## Investigate shared failure causes

Replicas can share power, networking, configuration or a software defect. A bad change rolled out everywhere may take every copy down together. A surviving replica may also overload when traffic shifts to it. Both mechanisms break the independent-failure model.

Separating failure domains reduces some shared infrastructure risks; it does not remove shared software risks. Review routing, failover capacity and deployment practice before using a replica count to promise an availability target.

> [!analogy] Real-world analogy: keys and spare keys
> A journey needing every key on a ring stops if one required key is missing. Spare copies of one key help only if one copy can still be reached.
>
> **How it maps:** Required keys resemble series dependencies; usable copies resemble redundant replicas. Losing the bag containing every copy is a shared failure.
>
> **Where it stops:** Services also have partial failures, recovery delays and changing capacity; physical keys do not model those dynamics.

## Key takeaways
- Decide whether all components or any one component must work.
- Multiplication assumes independent component states.
- Shared causes and inadequate failover can defeat redundancy.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
