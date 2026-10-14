---
id: arch-queue-burst-drain-budgets
title: Sizing burst queues and drain time
level: intermediate
minutes: 3
summary: Calculate queue growth and recovery time while distinguishing temporary bursts from sustained overload.
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

For example, start with an empty queue and take a 2-minute burst at 20,000 messages a second while workers drain 5,000 a second. During a burst, the queue grows by the difference between what arrives and what workers remove:

```formula
B = (A − D) × T
B = (20000 − 5000) /s × 120 s
B = 1800000
where
B: the peak backlog at the end of the burst, in messages
A: the arrival rate during the burst, here 20,000 messages per second (/s)
D: the drain rate: how many messages per second the workers finish, here 5,000/s
T: how long the burst lasts, in seconds (s): 2 minutes = 120 s
s: seconds
/s: per second
In words: 15,000 extra messages a second for 120 seconds piles up 1.8 million messages.
```

If traffic then drops to zero, the time to clear it is the backlog divided by the drain rate:

```formula
T_drain = B / (D − A_remaining)
T_drain = B / D when A_remaining = 0 /s
T_drain = 1800000 / (5000 /s)
T_drain = 360 s
where
T_drain: time to empty the queue, in seconds (s): 360 s = 6 minutes
B: the backlog, 1.8 million messages
D: the drain rate, 5,000 messages per second (/s)
A_remaining: ongoing arrival rate while clearing the queue, in messages per second; zero in this example. The first equation needs D greater than A_remaining, with constant rates and sufficient worker capacity.
s: seconds
/s: per second
In words: 1.8 million messages at 5,000 a second take 6 minutes to clear.
```

When arrivals continue, the smaller spare rate makes recovery slower. If ongoing arrivals stay at or above the completion rate, the backlog cannot clear under this constant-rate model.

It works when the client doesn't need the result immediately (an order confirmation can arrive by email). It doesn't fix a *sustained* overload: if input exceeds drain rate forever, the queue grows without bound. You need monitoring on queue age and a way to shed load.

## Key takeaways
- A durable queue permits asynchronous acceptance and a controlled worker drain rate.
- Backlog grows by arrivals minus completed work over the burst duration.
- Ongoing arrivals reduce the spare rate available for clearing a backlog.
- A queue cannot cure sustained overload: monitor age and bound admission or shed work.

## Further reading
- [Azure Architecture Center: Queue-Based Load Leveling](https://learn.microsoft.com/en-us/azure/architecture/patterns/queue-based-load-leveling)
