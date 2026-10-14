---
id: msg-bounded-consumer-backpressure
title: Bound buffers and propagate backpressure
level: advanced
minutes: 2
summary: Keep slow processing from exhausting memory and identify where upstream work actually slows.
sourceLesson: msg-ordering-backpressure
---

A broker can safely buffer more work than a worker’s process memory. The consumer must preserve that benefit rather than draining the broker into an unlimited local queue.

## Backpressure

**Backpressure** is any mechanism by which a slow downstream component tells upstream components to slow down. Without it, the gap in speed has to go somewhere: memory, until something crashes.

Three things can happen when a consumer cannot keep up:

1. **Buffer**: hold the excess in a queue. Fine for bursts, fatal for sustained overload.
2. **Drop or shed**: discard some work deliberately (sample metrics, reject low-priority requests with 429/503).
3. **Slow the producer**: block or reject at the source.

Good systems use all three in layers, with **bounded** buffers everywhere.

### Where backpressure lives in practice

- **Pull-based consumers** (Kafka, SQS) have it built in: a consumer can fetch less, leaving backlog in the broker within retention/capacity limits; this alone does not slow independent producers. The broker is the buffer.
- **Kafka consumer `pause()` / `resume()`**: if an internal work queue fills, pause fetching from some partitions while still calling `poll()` (so the consumer is not kicked out of the group), then resume.
- **Kafka producer**: records wait in `buffer.memory` (default 32 MiB). When it is full, `send()` blocks for up to `max.block.ms` (default 60 s), then throws. That is backpressure reaching your application thread.
- **RabbitMQ**: prefetch caps in-flight messages per consumer; *flow control* throttles fast publishers when internal components cannot keep up; separate memory/disk alarms can block publishing.
- **Reactive Streams** (Akka/Pekko Streams, Project Reactor, RxJava): the subscriber signals `request(n)` and the publisher may not exceed cumulative requested demand. Demand flows upstream explicitly.

> [!warning] Unbounded in-memory queues are the classic bug
> A consumer that reads from Kafka as fast as it can into an unbounded `LinkedBlockingQueue` for a thread pool has defeated the broker's backpressure. Memory fills, GC thrashes, the consumer misses heartbeats, the group rebalances, and the next consumer does the same. Always bound the internal queue.

## Key takeaways

- Bound internal worker queues so slow work remains buffered in the broker rather than consuming all memory.
- Pause fetching while still polling for consumer liveness, then resume when work capacity returns.
- Producer buffer limits, RabbitMQ credits/flow control and Reactive Streams demand can propagate slowness upstream.
- Fetching less does not itself throttle independent producers; capacity and retention still bound the broker buffer.

## Further reading

- [Kafka consumer (Confluent docs)](https://docs.confluent.io/platform/current/clients/consumer.html)
- [Reactive Streams specification](https://www.reactive-streams.org/)
