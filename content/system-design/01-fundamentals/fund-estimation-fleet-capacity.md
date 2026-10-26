---
id: fund-estimation-fleet-capacity
title: Turn workload estimates into a resilient fleet
level: intermediate
minutes: 3
summary: Use CPU time and concurrency to size capacity, then account for replicas, overhead, peaks and zone failure.
sourceLesson: fund-estimation
---

A traffic estimate becomes a fleet estimate only after you specify what consumes each resource. CPU work, concurrent connections and replicated writes are different constraints, and failure removes usable capacity.

## Worked example 4: servers needed

**Assumptions:** 50,000 req/s peak, each request uses ~20 ms of CPU, servers have 16 cores, target 60% utilisation.

```formula reference
n_s = (Q × t_cpu) / (c × u)
where
n_s: server count before adding failure redundancy; round up to whole servers
Q: peak requests per second
t_cpu: measured CPU time per request, in seconds
c: CPU cores per server
u: target CPU utilisation as a fraction, such as 0.6 for 60%
In words: compare the CPU work arriving each second with the work one server can do at the chosen utilisation. Then check memory, I/O, latency and survivor capacity separately.
```

These assumptions require about 105 servers before zone redundancy. If three evenly sized zones must survive losing one, the two remaining zones together need that capacity. Rounding to 53 servers per zone gives **159 servers total**. This is an illustrative CPU estimate, not a guarantee about I/O, memory or tail latency.

## Common pitfalls

- **Bits vs bytes.** Network speeds are in bits; storage is in bytes. A 1 Gbps raw link rate corresponds to 125 MB/s before overhead.
- **Forgetting peaks.** Average QPS sizes nothing; capacity must handle the peak.
- **Forgetting concurrency.** For connections and sessions, use Little's law: the number connected at once is the arrival rate multiplied by the time each stays online. For example, 50 million daily users connected for 30 minutes each implies about one million connections on average, before the peak factor.
- **Forgetting replication and overhead.** Three replicas triple storage; index and metadata overhead depends on the schema and storage engine; state an explicit allowance or measure it.
- **Forgetting growth.** Plan for at least the next 1–2 years.
- **False precision.** "4,629.6 QPS" signals you've missed the point. Say "about 5k".

> [!warning] Check your units at every step
> Write the unit next to every number. Most estimation errors are unit errors, not arithmetic errors.

## Key takeaways
- CPU-seconds arriving per second estimate busy cores; target utilisation determines usable capacity per server.
- Size the survivors for peak traffic when a whole zone fails, then provision the complete fleet.
- Connections require concurrency estimates, while replicated writes consume capacity on every required copy.
- Include units, peaks, overhead and growth; avoid false precision.

## Further reading
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Little’s Law (Marc Brooker)](https://brooker.co.za/blog/2018/06/20/littles-law.html)
- [Handling Overload (Google SRE)](https://sre.google/sre-book/handling-overload/)
