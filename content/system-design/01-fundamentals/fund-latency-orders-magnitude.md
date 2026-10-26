---
id: fund-latency-orders-magnitude
title: Compare latency orders of magnitude carefully
level: basic
minutes: 3
summary: Use hypothetical timings to spot important differences, then measure the actual workload before designing around them.
sourceLesson: fund-latency-throughput
---

A useful estimate distinguishes nanoseconds, microseconds and milliseconds. Otherwise a small-looking number can hide a much slower operation. A microsecond is a thousand nanoseconds; a millisecond is a thousand microseconds.

## Use a timing table as a hypothesis

The following values are **hypothetical exercise inputs**, not current hardware benchmarks:

| Operation | Assumed time |
|---|---|
| L1 cache reference | 1 ns |
| Main memory reference | 100 ns |
| Random SSD read | 100 µs |
| Same-datacentre round trip | 0.5 ms |
| HDD seek | 10 ms |
| Distant-region round trip | 70 ms |

Converting to a common unit shows that these operations can occupy very different scales. Under these assumptions, memory access is much cheaper than a random storage read, and a distant round trip costs far more than either. The useful conclusion is where to investigate, rather than a ratio to memorise.

> [!note] Content gap: reproducible measurements
> These assumed values do not come from one measured hardware and workload configuration. Do not use them as capacity promises. Measure payload size, access pattern, caching, concurrency and load on the intended system.

A request can pay an expensive operation many times. Several sequential distant calls may dominate its latency even when each carries few bytes. Batching, overlapping independent work or moving computation near the data can avoid those repeated waits.

## Access pattern matters

A storage device does not have one latency for every operation. A mechanical disk may need to move its head before a random read, whereas sequential access can stream nearby data. SSD behaviour also depends on size, load and device details. A network cache adds a network exchange even when its own data is in RAM.

Use the table to ask specific questions: is this request waiting on many random reads, a distant dependency, or a saturated resource? Validate the answer with timings and traces.

## Throughput can be high while latency is poor

Moving a large batch efficiently does not guarantee a fast first result. A bulk physical transfer can deliver a huge quantity per trip while taking hours to deliver any of it. That same distinction applies when buffering or batching network and storage work.

> [!analogy] Real-world analogy: a lorry carrying drives
> A lorry can carry many drives in one journey, but the recipient waits for the journey to finish.
>
> **How it maps:** Total data delivered per journey can imply high average throughput, while the time until delivery remains long. Bandwidth and latency answer different questions.
>
> **Where it stops:** Physical transfers have loading, handling and copying costs. They are useful only for suitable bulk jobs, not interactive requests.

## Key takeaways
- Compare durations in consistent units before deciding which cost matters.
- Illustrative timing tables suggest hypotheses; measure the actual workload and access pattern.
- Repeated sequential exchanges can dominate latency even with small payloads.
- High bulk throughput does not imply a quick first response.

## Further reading
- [Service Level Objectives (Google SRE)](https://sre.google/sre-book/service-level-objectives/)
- [The Tail at Scale (Dean and Barroso)](https://www.barroso.org/publications/TheTailAtScale.pdf)
