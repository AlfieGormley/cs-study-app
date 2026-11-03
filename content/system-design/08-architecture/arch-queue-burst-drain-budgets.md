---
id: arch-queue-burst-drain-budgets
title: Understanding burst queues and recovery
level: intermediate
minutes: 3
summary: Explain when a queue can absorb a burst and why sustained overload needs capacity or admission changes.
sourceLesson: arch-scaling-writes
---

Batching reduces write overhead, but bursts can still exceed database capacity. A queue buys time only when the workload can accept delayed completion and later spare capacity.

## Queues as buffers (load levelling)

Traffic is spiky, and databases have a fixed write capacity. A **queue between producers and the database** absorbs bursts so the database can work at a steady rate.

```
 spike: 20k/s        steady: 5k/s
 [API] ---> [ Queue ] ---> [Workers] -> [DB]
             backlog
             grows,
             then drains
```

- The API accepts the request, enqueues it durably, and returns `202 Accepted`.
- Workers pull at a rate the database can sustain.

A short burst can create a large backlog even if workers continue at their normal sustainable rate.

While arrivals exceed completed work, the backlog grows. Once arrivals slow, only spare worker capacity clears old work; if ongoing arrivals use all capacity, the backlog does not drain.

If arrivals stop completely, all worker capacity can clear old work. Continued arrivals leave less capacity for recovery.

When arrivals continue, the smaller spare rate makes recovery slower. If ongoing arrivals stay at or above the completion rate, the backlog cannot clear under this constant-rate model.

It works when the client doesn't need the result immediately (an order confirmation can arrive by email). It doesn't fix a *sustained* overload: if input exceeds drain rate forever, the queue grows without bound. You need monitoring on queue age and a way to shed load.

> [!analogy] Real-world analogy: A parcel depot
> Parcels wait at a depot when they arrive faster than vans can leave. The pile shrinks later only if the vans have spare carrying capacity.
>
> **How it maps:** The depot is the queue, arrivals are admitted work and departures are completed work. Storage buys time for a temporary burst.
>
> **Where it stops:** The comparison does not guarantee retention, delivery or a completion deadline. A finite depot cannot absorb permanent overload.

## Key takeaways
- A durable queue permits asynchronous acceptance and a controlled worker drain rate.
- Backlog grows by arrivals minus completed work over the burst duration.
- Ongoing arrivals reduce the spare rate available for clearing a backlog.
- A queue cannot cure sustained overload: monitor age and bound admission or shed work.

## Further reading
- [Azure Architecture Center: Queue-Based Load Leveling](https://learn.microsoft.com/en-us/azure/architecture/patterns/queue-based-load-leveling)
