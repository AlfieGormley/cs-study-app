---
id: rel-inflight-work-bulkhead-pools
title: In-flight work and bulkhead pools
level: intermediate
minutes: 4
summary: Explain how slowness occupies caller resources and isolate dependency pools.
sourceLesson: rel-overload-protection
---

The preceding queue model showed why latency rises near saturation. Now follow the resources held by that waiting work. A bulkhead reserves a bounded share for one dependency; it helps only if other shared resources are isolated too.

Two more facts worth carrying around:

**Little's law** links traffic, latency and concurrency for any stable system, whatever the arrival pattern:

```formula essential
L = λW
where
L: the average number of requests in flight (in the system at once)
λ: lambda, the arrival rate, in requests per second (req/s), here 1,000
W: the average time each request spends in the system, in seconds (s): 50 ms = 0.05 s, or 2 s
req/s: requests per second
s: seconds
In words: in-flight requests equal arrival rate times latency. At 1,000 req/s, a 50 ms latency keeps 50 requests in flight; a 2 s latency keeps 2,000 in flight.
```

So slowness alone exhausts threads and connections: the traffic didn't change, but the concurrent slots needed can exceed the available pools.

**Without rejection or abandonment, sustained arrivals above service capacity have no finite steady-state queue.** The queue grows at the gap between what arrives and what is served:

If 1,100 requests arrive each second but only 1,000 can finish, the queue keeps growing until admission, abandonment or the arrival rate changes. More memory postpones exhaustion; it does not restore a steady state.

The backlog and typical waiting time grow while that sustained imbalance continues; individual waits can still vary.

Past saturation, latency rises until requests time out. Callers retry, adding load. Work completes after the client has given up, so a busy server can produce almost no useful output. This is **congestive collapse**, and the patterns below exist to prevent it.

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

In software, a **bulkhead** isolates resources so one failing workload can't consume everything.

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

> [!analogy] Real-world analogy: watertight compartments in a ship
> Separate compartments limit how far water from one leak can spread.
>
> **How it maps:** A bounded resource pool confines the slots a troubled dependency can occupy, preserving other pools.
>
> **Where it stops:** Shared memory, CPUs or other dependencies can still transmit the failure. Separating one pool does not isolate the whole process.

## Key takeaways

- Little’s law relates stable average in-flight work, arrival rate and time in system.
- Without rejection or abandonment, sustained arrivals above capacity build an ever-growing queue.
- Separate pools, quotas, instances or cells contain resource exhaustion from a slow workload.

## Further reading

- [Using load shedding to avoid overload (AWS Builders' Library)](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/)
- [Handling overload (Google SRE book)](https://sre.google/sre-book/handling-overload/)
- [Bulkhead pattern (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead)
