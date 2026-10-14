---
id: arch-active-capacity-home-region-writes
title: Reserving active-region capacity and ownership
level: advanced
minutes: 3
summary: Calculate survivor headroom and route invariant-sensitive writes to a fenced authoritative owner.
sourceLesson: arch-multi-region
---

Active-passive prepares standby capacity. Active-active serves live traffic in every region, but each survivor must still absorb failures without inventing extra capacity.

## Active-active

Every region serves live traffic. Users are routed to the nearest healthy region (latency-based DNS, anycast, or a global load balancer).

```
  EU users         US users
     |                |
 [Region EU] <----> [Region US]
  reads +    async    reads +
  writes   replicate  writes
```

Pros: local serving can reduce latency and each region exercises a production path. Failure routing, data promotion and spare-capacity behavior still need separate tests; active-active does not exercise every failover scenario.

Cons: if both regions accept writes to the **same data**, you must handle **conflicts**. And each region needs spare capacity to absorb the other's traffic. In the simplest model (equal regions, equally loaded, load divides linearly), when one of N regions fails its traffic is shared by the N − 1 survivors, so each region can run at most at:

```formula
U_max = (N − 1) / N
U_max = (2 − 1) / 2 = 0.5 = 50 %
where
U_max: the highest safe normal utilisation of each region, as a fraction of its capacity
N: the number of equal active regions, here 2
%: per cent; 0.5 = 50 %
In words: with N regions, survive one failure by keeping each region at most (N − 1)/N busy: 50 % for two regions, about 67 % for three, 75 % for four.
```

With two regions, each must stay at or below 50% before losing one. Real designs need margin below this and must account for state, retries, caches and resource-specific bottlenecks.

### Avoiding conflicts: partition the writes

The simplest active-active design gives each piece of data a **home region**:

- A user's account lives in the region where they signed up; all writes for that user go there.
- Other regions can serve **reads** from asynchronous replicas, and forward writes to the home region.
- One authoritative writer avoids concurrent cross-region ownership if enforced through failover fencing. Local transactions still need concurrency control, and multi-record operations can require coordination.

This is often called *geo-partitioning*. CockroachDB, Spanner and DynamoDB-based designs commonly use it, and it lines up neatly with data residency.

### Browsing and reservation can differ

Ticket-seat browsing may use global replicas when the product accepts delayed availability. Selling a seat needs an atomic condition that admits exactly one successful reservation. Route that operation to its fenced home-region writer, or use a suitable consensus-based store with conditional updates. Strong reads alone do not serialise a later write. Preallocated exclusive seat ownership is another possibility, but transferring ownership must preserve the exclusivity rule.

## Key takeaways
- Active serving in every region does not exercise every failure-routing scenario.
- Equal regions need spare capacity for the failed region's load; the formula gives an ideal ceiling before margin.
- A home region gives each record one write owner while other regions can serve delayed read copies.
- Hard reservation invariants still require atomic conditions or transactions, not a fresh read followed by an unconditional write.

## Further reading
- [Azure Architecture Center: Geode pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/geodes)
- [AWS: DynamoDB global tables](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GlobalTables.html)
