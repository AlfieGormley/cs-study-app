---
id: cs1-interview-cache-failover-capacity
title: Size cache misses and surviving-zone capacity
level: basic
minutes: 3
summary: Only cache misses reach the database in this cache-aside estimate.
sourceLesson: cs1-interview-framework
---

Continue the hypothetical workload: peak traffic is 30,000 reads and 3,000 writes each second. This unit turns it into a cache-miss budget and a fleet that survives losing one availability zone.

### From QPS to machines

To turn a load into a machine count, divide peak load by what one unit handles, then add capacity headroom (spare capacity for failures and spikes). A cache in front of the database means only the misses reach it:

With a 90% cache hit rate, one read in ten reaches the database. Cache failure can expose the store to much more traffic, so evaluate both warm-cache and degraded operation.

How many database replicas that needs still depends on measured query capacity. For the app tier, start with representative load-test results at the required latency:

For illustration, suppose the measured peak requires 35 servers, including a small operating margin. With three equal zones, 18 servers per zone leaves 36 after any one zone fails. This only works if traffic can move and the dependencies can handle it.

The zone-loss factor comes from the surviving share of an evenly balanced fleet:

```formula reference
C_total = C_required Z / (Z − 1)
where
C_total: fleet capacity to provision, in requests per second
C_required: capacity the surviving fleet must supply, in requests per second
Z: number of equal-capacity availability zones, greater than one
In words: provision enough capacity that all but one of the equally sized zones can still serve the required load; reserve additional margin for operational uncertainty.
```

Add further headroom for deploys, uneven traffic and measurement error. The model assumes the surviving fleet can receive the displaced traffic and that its dependencies also have enough capacity.

> [!analogy] Real-world analogy: A closed checkout lane
> A shop with three checkout lanes needs the remaining two to handle the queue when one closes.
>
> **How it maps:** Zones are separate groups of capacity; a failure shifts demand onto the surviving groups.
>
> **Where it stops:** Computer workloads need routing and dependency capacity too, and zones are not always equally sized.

## Key takeaways

- Only cache misses reach the database in this cache-aside estimate.
- Use measured per-server capacity at the required latency.
- Size the surviving zones to carry peak traffic, with additional operational headroom.

## Further reading

- [System Design Primer: design approach](https://github.com/donnemartin/system-design-primer/blob/master/README.md)
- [AWS: static stability and availability zones](https://aws.amazon.com/builders-library/static-stability-using-availability-zones/)
