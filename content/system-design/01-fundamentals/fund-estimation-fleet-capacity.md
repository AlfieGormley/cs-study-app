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

```formula
C = Q × t_cpu
C = 50,000 /s × 0.020 s = 1,000
c_use = 16 × 0.6 = 9.6
n_s = C / c_use = 1,000 / 9.6 ≈ 105
where
C: the number of CPU cores kept busy on average (CPU-seconds of work arriving per second)
Q: requests per second at peak, 50,000
t_cpu: CPU time each request uses, 20 ms = 0.020 s
s: second
c_use: usable cores per server: 16 cores, of which we plan to use 60%
n_s: the number of servers needed
≈: approximately equal to (rounded up)
In words: work arriving per second divided by the work one server can comfortably do per second gives the number of servers. This is Little's law again: busy cores = arrival rate × CPU time per request.
```

Add N+2 or zone redundancy: if you run across 3 zones and must survive losing one, the two surviving zones must carry the whole load, so each zone needs half of the 105 servers' worth (about 53). Provision 3 × 53 ≈ 160 servers.

## Common pitfalls

- **Bits vs bytes.** Network speeds are in bits; storage is in bytes. 1 Gbps = 125 MB/s, not 1 GB/s.
- **Forgetting peaks.** Average QPS sizes nothing; capacity must handle the peak.
- **Forgetting concurrency.** For connections and sessions, use Little's law: the number connected at once is the arrival rate multiplied by the time each stays online. 50 M DAU online 30 minutes a day is about 1 M connected at once on average (50 M × 30 / 1,440 minutes in a day), not 50 M.
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
