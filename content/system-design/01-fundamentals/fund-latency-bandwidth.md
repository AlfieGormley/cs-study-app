---
id: fund-latency-bandwidth
title: Separate latency from bandwidth and capacity
level: basic
minutes: 5
summary: Identify whether parallel capacity, fewer round trips or a faster link addresses the actual performance limit.
sourceLesson: fund-latency-throughput
---

Two numbers describe the performance of almost any system:

- **Latency**: how long a single operation takes, from request to response. Measured in time (ms, µs).
- **Throughput**: how many operations complete per unit time. Measured in requests/s, MB/s, messages/s.

They are related but not the same thing, and confusing them leads to bad designs.

## The pipe analogy

Think of a water pipe. Latency is how long a drop takes to travel from one end to the other. Throughput is how much water comes out per second.

```
 latency: travel time along the pipe
 throughput: flow per second

 in  ==============================  out
     <---------- 100 ms ---------->
         carries 1,000 req/s
```

You can increase throughput by adding more pipes in parallel (more servers) without changing latency at all. For an illustrative London–New York link, assume a 70 ms round trip. Adding servers cannot remove its propagation delay, because distance sets a floor on latency. The time a signal needs just to travel a distance is:

```formula
t = d / v
t = 5,570 km / 200,000 km/s
t ≈ 0.028 s = 28 ms
where
t: the one-way propagation delay, the time the signal spends travelling, in seconds (s) or milliseconds (ms)
d: the distance travelled, in kilometres (km); here 5,570 km, the great-circle (shortest over the globe) distance from London to New York
v: the speed of light in optical fibre, about 200,000 km/s, roughly two-thirds of its 300,000 km/s speed in a vacuum
km: kilometre, 1,000 metres
s: second
ms: millisecond, one thousandth of a second
≈: approximately equal to (the result is rounded)
In words: the further the signal travels, the longer it takes, and nothing but a shorter path or faster medium can change that. London to New York costs at least 28 ms each way.
```

So a round trip (there and back) costs at least 2 × 28 = 56 ms before any processing. Real cable routes are longer than the great circle and pass through routers; the assumed 70 ms includes some of those additional costs. Adding servers changes none of this.

## Bandwidth-bound or latency-bound?

The pipe analogy gives a simple model for how long one transfer takes: a fixed cost for each round trip, plus the time to push the bytes through the pipe.

```formula
T ≈ k × RTT + D / B
where
T: the total time for the transfer or exchange, in seconds (s)
k: the number of round trips that must happen one after another (each waits for the previous reply)
RTT: round-trip time, the time for a message to go to the other end and a reply to come back, in s
D: the amount of data to send, in bits (multiply bytes by 8)
B: the bandwidth of the link, in bits per second (bps)
≈: approximately equal to; the model ignores server processing time and protocol overhead
In words: time is the round trips paid one after another plus the data divided by how fast the pipe carries it.
```

Example: fetching a 1 MB file (8,000,000 bits) in one round trip over a 100 Mbps link with a 70 ms RTT takes about 70 ms + 8,000,000 / 100,000,000 s = 70 ms + 80 ms = 150 ms. Both terms matter here; in the two extreme cases below, one term swamps the other.

Big transfers are **bandwidth-bound**: the size term dominates, so a fatter pipe or compression helps. Many small, sequential exchanges are **latency-bound**: the round-trip term dominates, so bandwidth upgrades do nothing and you must cut round trips (batching, parallelism, moving closer).

> [!warning] Throughput limits show up as latency
> Users rarely see "throughput exceeded". They see slow pages and timeouts, because the queue in front of the bottleneck is growing.

## Throughput in practice

Throughput depends on hardware, payload size, schema, batching, persistence, concurrency and the target latency percentile. A 10 Gbps link has a raw signalling rate equivalent to 1.25 GB/s before protocol overhead; that is not an application throughput guarantee.

> [!note] Content gap: verified throughput benchmarks
> Generic per-server rates for web APIs, PostgreSQL, Redis and Kafka are omitted. No reproducible workload and hardware configuration was provided for those figures, so they cannot be reliably verified as capacity guidance. Benchmark the intended workload and record its settings before using a rate in a design.

## Key takeaways
- Parallel servers increase throughput capacity without necessarily shortening one lightly loaded request.
- Large transfers are often bandwidth-bound; small sequential exchanges pay repeated round trips.
- Treat raw link speeds and per-server rates as inputs to measurement, not application guarantees.

## Further reading
- [The Tail at Scale (Dean and Barroso)](https://www.barroso.org/publications/TheTailAtScale.pdf)
- [Service Level Objectives (Google SRE)](https://sre.google/sre-book/service-level-objectives/)
