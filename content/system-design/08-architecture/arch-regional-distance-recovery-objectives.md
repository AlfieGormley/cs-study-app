---
id: arch-regional-distance-recovery-objectives
title: Budgeting distance and recovery objectives
level: advanced
minutes: 4
summary: Relate propagation delay, replication acknowledgement and RPO/RTO to a chosen regional failure model.
sourceLesson: arch-multi-region
---

A cloud region may offer several availability zones, each with separate infrastructure and possibly multiple data centres. A correctly configured multi-AZ workload can tolerate specified zone failures, but a region label alone does not guarantee application availability. So why go **multi-region**?

- **Disaster recovery**: whole regions do fail, or partially fail in ways that look total (control-plane outages, bad deploys of regional services, major network events).
- **Latency**: long paths impose propagation delay. Light in optical fibre travels at roughly two-thirds of its speed in a vacuum, about 200 km every millisecond, so distance alone sets a minimum delay (worked out below). Serving Australian users from Australia matters.
- **Data residency**: laws and contracts may require data about EU residents, or a particular government's citizens, to stay in specific places.

The minimum one-way delay over a fibre path is just distance divided by speed:

```formula
t = d / v
t = 17000 km / (200 km/ms) = 85 ms
where
t: the one-way propagation delay, in milliseconds (ms)
d: the length of the fibre path, in kilometres (km); here a hypothetical 17,000 km route
v: the speed of light in fibre, about 200 km per millisecond (km/ms), roughly two-thirds of its speed in a vacuum
km: kilometres
ms: milliseconds, thousandths of a second
In words: 17,000 km of fibre costs at least 85 ms each way, so at least 170 ms for a round trip, before any routing or equipment delay.
```

This is a floor, not a prediction: real routes are longer than the straight line, and routers and queues add more. Measure actual round-trip times (RTTs).

It's also expensive and hard. Extra regions add infrastructure and operating costs and, more importantly, force you to confront **the speed of light in your data layer**.

## The fundamental trade-off

Synchronous acknowledgment latency depends on required replicas, distance, storage and protocol. Benchmark the chosen deployment.

> [!note] Evidence gap
> Generic cross-AZ/region latency and recovery-time estimates are omitted because no measured deployment establishes them. Numeric quiz examples state hypothetical inputs.

That gives you a choice for each piece of data:

- **Synchronous cross-region replication**: can protect acknowledged commits from loss of one region when they are durably retained in a surviving region and failover selects the correct replica; this can meet a zero-loss objective for that failure model. Each required remote acknowledgment adds latency, and writes stop if the required remote acknowledgements or quorum become unreachable; a three-region quorum can continue after losing one region.
- **Asynchronous replication**: fast local writes, but a failure can lose acknowledged writes not yet durably replicated. Observed lag does not by itself guarantee a worst-case recovery point.

This is CAP and PACELC in practice: under a partition you choose consistency or availability, and even without one you choose latency or consistency.

Two numbers frame every DR design:

- **RPO** (recovery point objective): how much data you can afford to lose, measured in time.
- **RTO** (recovery time objective): how long you can be down.

## Key takeaways
- Distance creates a propagation floor; measured RTT includes routes, equipment and queues.
- Synchronous remote durability can protect acknowledged writes for a defined region-loss model at a coordination cost.
- Asynchronous replication risks unreplicated acknowledged writes; observed lag is not a worst-case loss bound.
- RPO targets allowable loss and RTO targets restoration time; validate both with recovery evidence.

## Further reading
- [AWS: Disaster recovery options in the cloud](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)
- [Azure Architecture Center: Geode pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/geodes)
