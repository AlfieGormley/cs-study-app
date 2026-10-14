---
id: rel-inflight-work-bulkhead-pools
title: In-flight work and bulkhead pools
level: intermediate
minutes: 4
summary: Calculate resource pressure from slowness and isolate dependency pools.
sourceLesson: rel-overload-protection
---

The preceding queue model showed why latency rises near saturation. Now follow the resources held by that waiting work. A bulkhead reserves a bounded share for one dependency; it helps only if other shared resources are isolated too.

Two more facts worth carrying around:

**Little's law** links traffic, latency and concurrency for any stable system, whatever the arrival pattern:

```formula
L = λW
L = 1,000 req/s × 0.05 s = 50
L = 1,000 req/s × 2 s = 2,000
where
L: the average number of requests in flight (in the system at once)
λ: lambda, the arrival rate, in requests per second (req/s), here 1,000
W: the average time each request spends in the system, in seconds (s): 50 ms = 0.05 s, or 2 s
req/s: requests per second
s: seconds
In words: in-flight requests equal arrival rate times latency. At 1,000 req/s, a 50 ms latency keeps 50 requests in flight; a 2 s latency keeps 2,000 in flight.
```

So slowness alone exhausts threads and connections: the traffic didn't change, but the concurrent slots needed went up forty-fold.

**Without rejection or abandonment, sustained arrivals above service capacity have no finite steady-state queue.** The queue grows at the gap between what arrives and what is served:

```formula
Q(t) = (λ − μ) × t
Q(60 s) = (1,100 − 1,000) req/s × 60 s
Q(60 s) = 6,000
where
Q(t): the extra requests queued after t seconds of overload
λ: lambda, the arrival rate, here 1,100 requests per second (req/s)
μ: mu, the service rate, the most requests per second the server can complete, here 1,000 req/s
t: the time the overload has lasted, in seconds (s), here 60 s
req/s: requests per second
s: seconds
In words: 100 more requests arrive each second than can be served, so after a minute 6,000 are waiting, and the queue keeps growing for as long as the overload lasts.
```

Every request waits longer than the one before until something gives.

Past saturation, latency rises until requests time out. Callers retry, adding load. Work completes after the client has given up, so the server does 100% work for 0% useful output. This is **congestive collapse**, and the patterns below exist to prevent it.

```
Goodput
  ▲      with shedding
  │   ┌───────────────
  │  ╱╲
  │ ╱  ╲ without
  │╱    ╲___________
  └──────────────────▶
       offered load
```

## Bulkheads

Ships are divided into watertight compartments (bulkheads) so one breach doesn't sink the vessel. In software, a **bulkhead** isolates resources so one failing workload can't consume everything.

Without bulkheads, a service with a 200-thread pool calling three dependencies can lose all 200 threads to the one dependency that's hanging:

```
Shared pool (200)      Bulkheads
┌───────────────┐   ┌─────┬─────┬─────┐
│ ████████████  │   │ A:80│ B:80│ C:40│
│ all stuck on C│   │ ok  │ ok  │stuck│
└───────────────┘   └─────┴─────┴─────┘
 everything down     only C's feature down
```

Bulkheads appear at many scales:

- **Thread or connection pools** per dependency.
- **Separate instances** for critical and non-critical traffic (e.g. checkout vs recommendations).
- **Per-tenant quotas**, so a noisy customer can't starve others.
- **Cells and shards**, the largest form of bulkhead (see the designing-for-failure lesson).

## Key takeaways

- Little’s law relates stable average in-flight work, arrival rate and time in system.
- Without rejection or abandonment, sustained arrivals above capacity build an ever-growing queue.
- Separate pools, quotas, instances or cells contain resource exhaustion from a slow workload.

## Further reading

- [Using load shedding to avoid overload (AWS Builders' Library)](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/)
- [Handling overload (Google SRE book)](https://sre.google/sre-book/handling-overload/)
- [Bulkhead pattern (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead)
