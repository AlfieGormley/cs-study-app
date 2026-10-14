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

```formula
db reads = reads × (1 − h)
db reads = 30,000/s × (1 − 0.9)
db reads = 3,000/s
where
db reads: reads per second that reach the database
reads: peak reads per second arriving at the service
h: the cache hit rate, the fraction of reads answered by the cache, between 0 and 1; here 90% = 0.9
/s: per second
In words: with a 90% hit rate only one read in ten reaches the database, so 30,000 reads a second becomes 3,000.
```

How many database replicas that needs still depends on measured query capacity. For the app servers, assume each handles 1,000 requests a second (an assumption you would measure):

```formula
servers = load / capacity
servers = 33,000/s / (1,000/s) = 33
total = 35 × Z / (Z − 1)
total = 35 × 3 / 2 = 52.5 → 54
where
load: peak requests per second for the app tier, here 30,000 reads + 3,000 writes = 33,000/s
capacity: requests per second one server handles, here an assumed 1,000/s
servers: servers needed at peak with nothing broken: 33, rounded up to 35 for a little headroom before the zone sum
Z: the number of availability zones (separate data-centre sites) the fleet is spread over, here 3
total: servers to run so that losing one whole zone still leaves enough
→: "round up to", here to 54 so the three zones get 18 each
/s: per second
In words: 33 servers' worth of load, rounded to 35, spread over three zones needs about 54 servers so that if one zone fails, the remaining 36 can still carry the peak.
```

The zone-loss factor comes from the surviving share of an evenly balanced fleet:

```formula
f = (Z − 1) / Z
k = 1 / f = Z / (Z − 1)
where
f: the fraction of fleet capacity surviving one complete zone loss, dimensionless
Z: the number of equal-capacity zones, greater than one
k: the multiplier on bare required capacity, dimensionless
In words: losing one of three equal zones leaves two thirds of the capacity, so provision one and a half times the bare requirement.
```

Add further headroom for deploys, uneven traffic and measurement error. The model assumes the surviving fleet can receive the displaced traffic and that its dependencies also have enough capacity.

## Key takeaways

- Only cache misses reach the database in this cache-aside estimate.
- Use measured per-server capacity at the required latency.
- Size the surviving zones to carry peak traffic, with additional operational headroom.

## Further reading

- [System Design Primer: design approach](https://github.com/donnemartin/system-design-primer/blob/master/README.md)
- [AWS: static stability and availability zones](https://aws.amazon.com/builders-library/static-stability-using-availability-zones/)
