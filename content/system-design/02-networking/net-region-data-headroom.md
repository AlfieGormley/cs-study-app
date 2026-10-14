---
id: net-region-data-headroom
title: "Replication risk and failover headroom"
level: advanced
minutes: 4
summary: "Compare active regional layouts and size survivors for both even and uneven inherited traffic."
sourceLesson: net-global-traffic
---
A routing change only helps if the surviving region has the data and spare capacity to serve it. Work out the replication failure model before calculating how much load can move.

## Multi-region failover

Routing is the easy part. The hard part is what happens to **data and capacity** when you move traffic.

### Active-passive vs active-active

| | Active-passive | Active-active |
|---|---|---|
| Normal traffic | One region | All regions |
| Standby cost | Idle capacity | Shared |
| Failover | Promote standby | Shift traffic |
| Data | Often an async standby; synchronous designs are possible | Can use one write leader, partitioned ownership or multi-region coordination |
| Risk | Standby untested | Conflicts, complexity |

**Active-passive** is simpler: one region serves, another holds replicated data. But failover is a rare, scary event. The standby may have drifted, its caches are cold, and the replica may lag. **RPO** is the recovery-point objective, expressed as a time window; actual lag and recovery behavior determine whether that objective is met.

**Active-active** serves from every region all the time, so failover is "just" sending more traffic to regions that are already working. The application tier may be active in several regions while writes still go to one database leader, at the cost of cross-region latency. Local writes in every region require distributed coordination, conflict handling or ownership partitioning, covered in the consistency module.

### Capacity planning for failover

If you run three regions at 70% utilisation and one fails, its traffic lands on the other two. In an ideal model with equal region capacities, proportional work, no extra failover overhead and even redistribution, the arithmetic is:

```formula
u_after = N × u / (N − 1)
u_after = 3 × 70% / 2 = 105%
u_max = (N − 1) / N × 100%
u_max = 2 / 3 × 100% ≈ 66.7%
where
u_after: the utilisation of each surviving region after one region fails and its load is shared evenly, as a percentage of that region's capacity
N: the number of regions, all with the same capacity; here 3
u: each region's utilisation before the failure, as a percentage of its capacity; here 70%
u_max: the highest utilisation you can run each region at and still stay at or below 100% after losing one region
%: per cent of a region's capacity
≈: approximately equal to
In words: the total load (here 210% of one region) must fit in one region fewer, so each region can normally run at most (N − 1)/N full.
```

So three regions at 70% each become two regions at 105%: overloaded. The formula gives the ideal no-overload ceiling before losing one region: **about 66% for three regions**, 50% for two and 80% for five. Use a lower target when latency SLOs, cold caches or other bottlenecks require spare capacity. (This assumes traffic redistributes evenly. With GeoDNS or anycast it often doesn't: a failed EU region's users may mostly land in the next-nearest region, which needs more headroom than the average.)

For loss of the primary region, writes acknowledged before reaching an asynchronous standby may be lost; the lag window and write rate determine how many are at risk. Acknowledging only after the write is durably recorded in a surviving region can protect that failure model, while adding remote coordination latency and availability coupling. This does not guarantee survival of correlated loss, corruption or mistaken deletion; RPO remains a time objective, not a write count.

## Key takeaways

- Active-passive trades simplicity for standby readiness risk; active-active still needs a deliberate write ownership model.
- Asynchronous replication can lose acknowledged writes if the only copy is in a permanently lost region.
- The equal-split headroom rule is an ideal ceiling; plan each region for the load its routing actually inherits.

## Further reading

- [Disaster recovery options in the cloud (AWS)](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)
- [Latency-based routing (Amazon Route 53)](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy-latency.html)
