---
id: fund-concurrency-pool-sizing
title: Size concurrency pools with Little’s law
level: intermediate
minutes: 4
summary: Calculate busy threads and connections, and predict why a slow dependency exhausts a pool.
sourceLesson: fund-scalability
---

Thread and connection pools limit how many requests can hold a resource at once. Little’s law estimates their average occupancy and shows what changes when a downstream call becomes slow.

## Little's law: concurrency, throughput, latency

Little's law is one of the most useful equations in capacity planning. For any stable system (one where the queue doesn't grow forever), averaged over a long enough time:

```formula
L = λ × W
where
L: the average number of items in the system at once (requests in flight, busy threads, open connections); a plain count
λ: lambda, the average arrival rate, which in a stable system equals the throughput, in items per second (/s)
W: the average time each item spends inside the system, in seconds (s)
s: second
In words: the number of things inside equals how fast they arrive multiplied by how long each one stays.
```

It holds regardless of arrival distribution, and applies to a single thread pool, a whole service or a coffee shop.

**Example 1: sizing a thread pool.** A service handles 2,000 req/s, and each request spends 50 ms in the service (much of it waiting on the database):

```formula
L = λ × W
L = 2,000 /s × 0.050 s = 100
where
L: the average number of requests in the service at once
λ: lambda, the arrival rate, 2,000 requests per second (/s)
W: the time each request spends in the service, 50 ms = 0.050 s
s: second
In words: 2,000 requests arriving every second, each staying a twentieth of a second, means about 100 inside at any moment.
```

With one thread per request, you need at least ~100 threads (plus headroom).

**Example 2: database connections.** 5,000 queries/s at 4 ms each:

```formula
L = 5,000 /s × 0.004 s = 20
where
L: the average number of database connections busy at once
s: second; 4 ms = 0.004 s is how long each query holds a connection
In words: 5,000 queries a second, each holding a connection for 4 ms, keep about 20 connections busy.
```

A pool of 30–40 is a starting hypothesis, not a guarantee: burstiness, latency tails and database capacity determine the necessary headroom. A pool of 500 per app instance across 50 instances permits 25,000 connections and can impose substantial overhead; validate the total against database capacity rather than assuming more connections help.

**Example 3: what happens when latency rises.** The database slows from 4 ms to 40 ms while traffic stays at 5,000/s:

```formula
L = 5,000 /s × 0.040 s = 200
where
L: the average number of database connections needed at once
s: second; 40 ms = 0.040 s is the new time each query holds a connection
In words: the same traffic held ten times as long needs ten times as many connections.
```

The pool of 40 is exhausted; requests queue, latency rises further, and the problem cascades. Little's law explains why a slow dependency causes thread or connection-pool exhaustion upstream, and why timeouts and bulkheads (reliability module) matter.

## Key takeaways
- Average concurrency equals average arrival rate multiplied by average time inside a stable system.
- Use the time spent holding the resource you are sizing, with seconds matching the per-second rate.
- Longer resource occupancy requires more concurrency; pool headroom and database capacity must be measured.

## Further reading
- [Little’s Law (Marc Brooker)](https://brooker.co.za/blog/2018/06/20/littles-law.html)
- [Handling Overload (Google SRE)](https://sre.google/sre-book/handling-overload/)
