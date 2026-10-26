---
id: fund-latency-bandwidth
title: Separate latency from bandwidth and capacity
level: basic
minutes: 4
summary: Identify whether parallel capacity, fewer round trips or a faster link addresses the actual performance limit.
sourceLesson: fund-latency-throughput
---

Two numbers describe the performance of almost any system:

- **Latency**: how long a single operation takes, from request to response. Measured in time (ms, µs).
- **Throughput**: how many operations complete per unit time. Measured in requests/s, MB/s, messages/s.

They are related but not the same thing, and confusing them leads to bad designs.

## The pipe analogy

> [!analogy] Real-world analogy: parallel water pipes
> A longer pipe delays the first arriving drop. More pipes can carry more water at once.
>
> **How it maps:** Latency is the travel time; throughput is the amount delivered each second. Parallel servers can add capacity without shortening one request's journey.
>
> **Where it stops:** Networks carry packets and servers queue work; their delays depend on contention and processing as well as distance.

```
 latency: travel time along the pipe
 throughput: flow per second

 in  ==============================  out
     <---------- 100 ms ---------->
         carries 1,000 req/s
```

You can increase throughput by adding servers without shortening a lightly loaded request. For an illustrative London–New York link, assume a 70 ms round trip. A signal still has to travel there and back; adding servers cannot remove that propagation delay. Moving work closer or avoiding an exchange can help.

## Bandwidth-bound or latency-bound?

The pipe analogy gives a simple model for how long one transfer takes: a fixed cost for each round trip, plus the time to push the bytes through the pipe.

```formula reference
T ≈ k × RTT + D / B
where
T: the total time for the transfer or exchange, in seconds (s)
k: the number of round trips that must happen one after another (each waits for the previous reply)
RTT: round-trip time, the time for a message to go to the other end and a reply to come back, in s
D: the amount of data to send, in bits (multiply bytes by 8)
B: the bandwidth of the link, in bits per second (bps)
≈: approximately equal to; the model ignores server processing time and protocol overhead
In words: transfer time includes the round trips that must finish one after another, plus the time needed to send all the data at the available bandwidth.
```

For example, under this simplified model a 1 MB file over a 100 Mbps link with one 70 ms round trip takes about 150 ms. Sending the bytes and waiting for the reply both matter; server processing, protocol overhead and congestion would add more delay.

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
