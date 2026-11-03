---
id: rel-regional-failover-fencing-lag
title: Regional failover, fencing and lag
level: intermediate
minutes: 4
summary: Audit failover for stale writers, lost writes, routing delays and survivor capacity.
sourceLesson: rel-disaster-recovery
---

The previous units selected recovery objectives and a strategy. Failover mechanics determine whether the promise holds during a real incident. Fencing prevents a still-alive former primary from writing; it does not itself copy missing acknowledged data.

## Failover mechanics

Failover deserves explicit testing. Key questions:

- **Who decides?** Automatic failover reacts fast but can flap or trigger on false positives (a network partition makes the primary *look* dead). Many teams automate the mechanics but require a human to press the button for regional failover.
- **Split brain**: if the old primary isn't truly dead, two primaries accept writes. Use **fencing** to stop the old primary's writes before promoting. Enforce the fence at the storage or write authority, including existing sessions; a credential revocation counts only once its effect is verified.
- **Capacity in the target**: the surviving region must take the whole load. For equal-capacity regions with evenly redistributed traffic and tolerance of one region loss, the pre-failure utilisation ceiling is the fraction of regions that survive: 50% for two regions and about 67% for three. Reserve additional headroom for the desired latency.
- **DNS TTLs**: clients cache DNS. A freshly cached 300 s record can remain valid for five minutes; existing connections and client caching behavior can extend recovery. Preconfigured global routing can avoid waiting for DNS changes, but detection and reconnection still take time.
- **Data loss on promotion**: with async replication, writes that hadn't replicated are lost. That gap is the observed recovery-point loss; the RPO is the target it must meet.
- **Failback**: returning to the original region is a second migration, often forgotten in the plan.

The capacity ceiling for surviving the loss of one of several equal regions:

Two equal regions tolerating either region’s loss each need capacity for the full load. With three equal regions tolerating one loss, any two must carry it. Leave additional room for traffic imbalance and target latency.

How much data an asynchronous failover loses depends on how far behind the replica was at that moment:

More lag means more acknowledged work may be absent from the promoted copy. A typical or p99 lag is not a worst-case bound; inspect the recoverable point at failover and compare it with the business target.

Lag is not constant: it often grows during exactly the load spikes and network trouble that precede a disaster, so plan for the worst lag you have measured, not the average.

> [!tip] Avoid control-plane dependencies during failover
> AWS's guidance is to rely on *data-plane* operations for failover (e.g. Route 53 health checks and pre-configured routing, which keep working) rather than control-plane actions like creating resources or editing records, which may be impaired during a regional event.

## Key takeaways

- Fence a former primary before promoting a replacement and rehearse failback too.
- Size already-running survivors for full target demand with latency headroom.
- Account for replication lag at the actual failure, DNS caching and reconnects; preconfigure data-plane restoration routes.

## Further reading

- [Disaster recovery options in the cloud (AWS whitepaper)](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)
- [Data integrity: what you read is what you wrote (Google SRE book)](https://sre.google/sre-book/data-integrity/)
