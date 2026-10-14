---
id: msg-stream-watermarks-late-results
title: Watermarks, idleness and late-result updates
level: advanced
minutes: 3
summary: Balance fast window output with late corrections and a sink that replaces updated results.
sourceLesson: msg-stream-processing
---

Event-time windows need a decision about when to emit and when to stop accepting corrections. A watermark is progress information, not proof that no delayed event exists.

## Watermarks

In event time, how does an operator know that the 09:00–09:01 window is complete? It cannot know for sure; an event could always be delayed. An **event-time watermark** (usually just called a watermark) is a timestamp the processor attaches to its progress, meaning: "I believe no more events with a timestamp at or before this one will arrive." When the watermark passes the end of a window, the window fires.

The simplest and most common strategy is **bounded out-of-orderness**: assume no event arrives more than a fixed delay behind the newest one seen so far.

```formula
W ≈ t_max − δ
W ≈ 09:01:12 − 10 s = 09:01:02
where
W: the watermark: the event time up to which the processor believes it has seen everything
t_max: the largest event timestamp seen so far, here 09:01:12
δ: delta, the allowed delay (the out-of-orderness bound), here 10 seconds
≈: approximately equal to; Flink's generator subtracts one more millisecond and emits the value periodically
s: seconds
In words: the watermark trails the newest event time by the allowed delay, so events up to 10 seconds out of order still count.
```

Here W has passed 09:01:00, the end of the 09:00–09:01 window, so that window can fire. This is a conceptual formula: Flink's bounded generator actually produces 09:01:01.999.

This Flink API fragment needs imports, an `Order` type and attachment to the source. It describes watermark configuration, not a complete running job or a fixed wall-clock output.

```java
WatermarkStrategy
  // Trail observed event time by this
  // bound.
  .<Order>forBoundedOutOfOrderness(
      Duration.ofSeconds(10))
  // Extract the business event timestamp.
  .withTimestampAssigner(
      (o, ts) -> o.eventTimeMillis())
  // Exclude inputs silent for this
  // interval.
  .withIdleness(Duration.ofMinutes(1));
```

Two important subtleties:

- **Watermarks are the minimum across inputs.** An operator reading 8 Kafka partitions advances its watermark only as fast as the slowest partition. One **idle partition** with no data holds the watermark back and no window ever fires. `withIdleness` marks such sources idle so they are ignored.
- **The delay is a trade-off.** A larger delay gives more complete results but higher latency. A smaller delay gives lower latency but more late events.

### Late data

An event that arrives after the watermark has passed its window is **late**. Options:

1. **Drop it** (default in Flink after the window cleanup time is reached).
2. **Allowed lateness**: keep window state for extra time and emit an **updated result** when a late event arrives. Downstream must handle updates (upserts, not appends).
3. **Side output**: route late events to a separate stream for correction or auditing.

Kafka Streams expresses this as a **window grace period** (for example `TimeWindows.ofSizeAndGrace(Duration.ofMinutes(1), Duration.ofSeconds(30))`), and by default emits updated results continuously; `suppress(untilWindowCloses)` emits only the final result.

> [!tip] The Dataflow model
> Google's Dataflow paper frames all of this as four questions: **what** are you computing, **where** in event time (windows), **when** in processing time are results emitted (watermarks and triggers), and **how** do refinements relate (discard or accumulate). Apache Beam implements it directly.

## Key takeaways

- Watermarks estimate event-time completeness and progress only as fast as the active input minimum.
- Idleness detection keeps silent inputs from holding every window open indefinitely.
- Allowed lateness retains state and can emit corrected results; upsert by window and key rather than append totals.
- Finality depends on event-time progress and durable output, not wall-clock age alone.

## Further reading

- [Timely stream processing: event time and watermarks (Apache Flink docs)](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/)
- [Windows (Apache Flink docs)](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/operators/windows/)
- [The Dataflow Model (Google Research)](https://research.google/pubs/the-dataflow-model-a-practical-approach-to-balancing-correctness-latency-and-cost-in-massive-scale-unbounded-out-of-order-data-processing/)
