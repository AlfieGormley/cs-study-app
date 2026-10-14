---
id: rel-regional-failover-fencing-lag
title: Regional failover, fencing and lag
level: intermediate
minutes: 4
summary: Audit failover for stale writers, lost writes, routing delays and survivor capacity.
sourceLesson: rel-disaster-recovery
---

The previous units selected a recovery target and a strategy. Failover mechanics determine whether the promise holds during a real incident. Fencing prevents a still-alive former primary from writing; it does not itself copy missing acknowledged data.

## Failover mechanics

Failover deserves explicit testing. Key questions:

- **Who decides?** Automatic failover reacts fast but can flap or trigger on false positives (a network partition makes the primary *look* dead). Many teams automate the mechanics but require a human to press the button for regional failover.
- **Split brain**: if the old primary isn't truly dead, two primaries accept writes. Use **fencing** to stop the old primary's writes before promoting. Enforce the fence at the storage or write authority, including existing sessions; a credential revocation counts only once its effect is verified.
- **Capacity in the target**: the surviving region must take the whole load. For equal-capacity regions with evenly redistributed traffic and tolerance of one region loss, the pre-failure utilisation ceiling is the fraction of regions that survive (see the formula below): 50% for two regions and about 67% for three. Reserve additional headroom for the desired latency.
- **DNS TTLs**: clients cache DNS. A freshly cached 300 s record can remain valid for five minutes; existing connections and client caching behavior can extend recovery. Preconfigured global routing can avoid waiting for DNS changes, but detection and reconnection still take time.
- **Data loss on promotion**: with async replication, writes that hadn't replicated are lost. That gap is the observed recovery-point loss; the RPO is the target it must meet (see the formula below).
- **Failback**: returning to the original region is a second migration, often forgotten in the plan.

The capacity ceiling for surviving the loss of one of several equal regions:

```formula
U_max = (R − 1) / R
U_max = (2 − 1) / 2 = 50%
U_max = (3 − 1) / 3 ≈ 67%
where
U_max: the highest utilisation each region can run at before the failure, so the survivors are at no more than 100% afterwards
R: the number of equal-capacity regions, here 2 or 3
≈: approximately equal to (rounded)
%: per cent of one region's capacity
In words: the share of regions left standing is the share of capacity you can use day to day.
```

How much data an asynchronous failover loses depends on how far behind the replica was at that moment:

```formula
N_lost = r × t_lag
N_lost = 2,000 writes/s × 3 s = 6,000 writes
where
N_lost: the acknowledged writes lost when the replica is promoted
r: the constant acknowledged-write rate over the lag interval on the old primary, here 2,000 writes per second (writes/s)
t_lag: the replication lag at the moment of failure, in seconds (s), here 3 s
writes/s: writes per second
s: seconds
In words: a replica 3 seconds behind a primary taking 2,000 writes a second loses about 6,000 writes on promotion. The observed data loss is 3 seconds; it meets the RPO only if the RPO is at least 3 seconds.
```

Lag is not constant: it often grows during exactly the load spikes and network trouble that precede a disaster, so plan for the worst lag you have measured, not the average.

> [!tip] Avoid control-plane dependencies during failover
> AWS's guidance is to rely on *data-plane* operations for failover (e.g. Route 53 health checks and pre-configured routing, which keep working) rather than control-plane actions like creating resources or editing records, which may be impaired during a regional event.

## Key takeaways

- Fence a former primary before promoting a replacement and rehearse failback too.
- Size already-running survivors for full target demand with latency headroom.
- Account for replication lag at the actual failure, DNS caching and reconnects; preconfigure data-plane recovery paths.

## Further reading

- [Disaster recovery options in the cloud (AWS whitepaper)](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)
- [Data integrity: what you read is what you wrote (Google SRE book)](https://sre.google/sre-book/data-integrity/)
