---
id: net-region-data-headroom
title: "Replication risk and failover headroom"
level: advanced
minutes: 4
summary: "Compare active regional layouts and plan survivor headroom for both even and uneven inherited traffic."
sourceLesson: net-global-traffic
---
A routing change only helps if the surviving region has the data and spare capacity to serve it. Decide what the replication model can lose, then check that survivors can absorb the traffic that will actually arrive.

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

If you run three equal regions at 70% utilisation and one fails, its traffic lands on the other two. Spread evenly, each survivor takes an extra 35 points and runs at about 105%: overloaded, before autoscaling has had time to react. The rule behind this is that the total load must still fit into one region fewer:

```formula essential
u_max = (N − 1) / N
where
u_max: the highest normal utilisation, as a fraction of each region's capacity, that still fits after losing one region
N: the number of regions, all with equal capacity
In words: to survive losing one of N equal regions with an even spread, each may normally run at most (N − 1)/N full: about two-thirds with three regions, half with two and 80% with five.
```

This is an ideal ceiling. It assumes equal capacities, load proportional to work, no extra failover overhead and an even redistribution. Use a lower target when latency SLOs, cold caches or other bottlenecks need spare capacity. Above all, redistribution is rarely even: with GeoDNS, latency routing or anycast, a failed EU region's users may mostly land in the *next-nearest* region, which then needs far more headroom than the average suggests. Plan each region for the traffic it would actually inherit.

### Acknowledged writes at risk

For loss of the primary region, writes acknowledged before reaching an asynchronous standby may be lost; the lag window and write rate determine how many are at risk. Acknowledging only after the write is durably recorded in a surviving region can protect that failure model, while adding remote coordination latency and availability coupling. This does not guarantee survival of correlated loss, corruption or mistaken deletion; RPO remains a time objective, not a write count.

## Key takeaways

- Active-passive trades simplicity for standby readiness risk; active-active still needs a deliberate write ownership model.
- Asynchronous replication can lose acknowledged writes if the only copy is in a permanently lost region.
- The equal-split headroom rule is an ideal ceiling; plan each region for the load its routing actually inherits.

## Further reading

- [Disaster recovery options in the cloud (AWS)](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)
- [Latency-based routing (Amazon Route 53)](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy-latency.html)
