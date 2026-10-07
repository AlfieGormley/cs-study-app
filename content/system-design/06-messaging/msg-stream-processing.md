---
id: msg-stream-processing
title: Stream processing: windows, time and state
level: advanced
minutes: 15
summary: How stream processors such as Flink and Kafka Streams compute over unbounded data: event time vs processing time, windows, watermarks, late data and fault-tolerant state.
---

A consumer that reads one message and writes one result is simple. Real-time analytics needs more: "orders per minute per region", "alert if a card is used in two countries within 10 minutes", "join each click with the ad impression that caused it". These need **stream processing**: continuous computation over unbounded data, with **windows**, **time** and **state**.

## Stateless vs stateful operators

- **Stateless**: each record is handled alone. `filter`, `map`, `flatMap`, routing. Easy to scale and restart.
- **Stateful**: the result depends on earlier records. Counts, sums, windows, joins, deduplication, pattern detection. State must be stored, partitioned by key, and survive crashes.

Almost all the difficulty, and value, lies in stateful processing.

## Event time vs processing time

Distinguish these time concepts; timestamps must actually be recorded or assigned to use them:

| Time | Meaning |
|---|---|
| Event time | When it happened (on the device) |
| Ingestion time | When the broker received it |
| Processing time | When the operator sees it |

They differ, sometimes wildly. A phone on the Underground records a tap at 09:00:05 and uploads it at 09:12:40. A consumer restarting after an outage processes an hour of backlog in five minutes.

```
event time  ──────────────▶
             a  b  c     d
processing   b  a     d  c
time        ──────────────▶
```

If you window by **processing time**, "orders between 09:00 and 09:01" means "orders my job happened to read then", so results change if you replay, and backlogs pile into a single window. With **event time**, window membership follows the recorded event timestamp rather than processing speed. Reproducible final results also require deterministic processing and the same accepted inputs and lateness policy; watermark-driven late-data drops can differ on replay. You must decide **how long to wait** for stragglers. That decision is what watermarks are for.

> [!note] The rule
> Use event time whenever results should mean something about the real world or must be reproducible on replay. Processing time can fit wall-clock scheduling and latency-oriented applications where arrival-time semantics are intended; it is not restricted to pipeline metrics.

## Windows

Windows chop an unbounded stream into finite chunks to aggregate.

### Tumbling

Fixed size, no overlap. Every event belongs to exactly one window.

```
|--1m--|--1m--|--1m--|
 ••  •   •••    •  •
```

Use for regular reports: per-minute counts, hourly billing.

### Hopping (Flink calls these "sliding")

Fixed size, advancing by a smaller step, so windows overlap. A 5-minute window every 1 minute puts each event in 5 windows.

```
|-----5m-----|
  |-----5m-----|
    |-----5m-----|
 ─1m─▶
```

Use for smoothed moving metrics: "requests in the last 5 minutes, updated every minute". Each event has size ÷ step window memberships when the dimensions divide evenly; actual state and CPU costs depend on incremental aggregation and shared panes.

Kafka Streams also has a distinct **sliding window** that is defined by a maximum time difference between records (used for "two events within 10 minutes of each other"), and windows are only created when records arrive.

### Session

Windows defined by **activity gaps** rather than the clock. A session closes after a gap of inactivity (say 30 minutes) and can be any length. Sessions for the same key **merge** when a late event bridges two of them.

```
user u1: ••• •    ••  •••
         └─s1─┘   └─s2──┘
              ≥30m gap
```

Use for user behaviour analytics: session length, pages per visit.

### Global and count windows

A single window for all time (with custom triggers), or windows of N records. Less common in system design discussions.

## Watermarks

In event time, how does an operator know that the 09:00–09:01 window is complete? It cannot know for sure; an event could always be delayed. A **watermark** is the processor's declaration: "I believe no more events with timestamp ≤ T will arrive." When the watermark passes the end of a window, the window fires.

The simplest and most common strategy is **bounded out-of-orderness**:

`watermark ≈ max event time seen − allowed delay`

Flink's bounded generator subtracts one additional millisecond and emits periodically, so this is a conceptual formula.

With a 10-second delay, after seeing an event at 09:01:12 the watermark is 09:01:02, so the 09:00–09:01 window can fire.

```java
WatermarkStrategy
  .<Order>forBoundedOutOfOrderness(
      Duration.ofSeconds(10))
  .withTimestampAssigner(
      (o, ts) -> o.eventTimeMillis())
  .withIdleness(Duration.ofMinutes(1));
```

Two important subtleties:

- **Watermarks are the minimum across inputs.** An operator reading 8 Kafka partitions advances its watermark only as fast as the slowest partition. One **idle partition** with no data holds the watermark back and no window ever fires. `withIdleness` marks such sources idle so they are ignored.
- **The delay is a trade-off.** Larger delay = more complete results, higher latency. Smaller delay = lower latency, more late events.

### Late data

An event that arrives after the watermark has passed its window is **late**. Options:

1. **Drop it** (default in Flink after the window cleanup time is reached).
2. **Allowed lateness**: keep window state for extra time and emit an **updated result** when a late event arrives. Downstream must handle updates (upserts, not appends).
3. **Side output**: route late events to a separate stream for correction or auditing.

Kafka Streams expresses this as a window **grace period** (for example `TimeWindows.ofSizeAndGrace(Duration.ofMinutes(1), Duration.ofSeconds(30))`), and by default emits updated results continuously; `suppress(untilWindowCloses)` emits only the final result.

> [!tip] The Dataflow model
> Google's Dataflow paper frames all of this as four questions: **what** are you computing, **where** in event time (windows), **when** in processing time are results emitted (watermarks and triggers), and **how** do refinements relate (discard or accumulate). Apache Beam implements it directly.

## Fault-tolerant state

Stateful operators hold a lot of state: millions of keys, each with a running count or a window buffer. It must survive crashes **and** be consistent with the input position, otherwise a restart double-counts.

### Flink: checkpoints

- State lives locally per parallel task, in memory or in **RocksDB** on local disk for large state (terabytes across a cluster is normal).
- Periodically, the JobManager injects **checkpoint barriers** into the sources. In aligned checkpoints, an operator coordinates input barriers and snapshots state to configured durable storage such as S3 or HDFS. Unaligned checkpoints also capture in-flight channel data to reduce alignment delay. This is a variant of the Chandy–Lamport distributed snapshot algorithm.
- A checkpoint records **state plus source offsets** together. On failure, Flink restores every operator from the last checkpoint and rewinds the sources to the matching offsets.
- With transactional sinks (for example, the Kafka sink using two-phase commit tied to checkpoints), this gives end-to-end exactly-once.
- **Savepoints** are manually triggered checkpoints for upgrades and rescaling.

### Kafka Streams: changelog topics

- Tasks maintain the stores defined by their topology; persistent stores commonly use RocksDB, while in-memory stores also exist. A task can have multiple stores and inputs.
- Fault-tolerant stores normally use Kafka changelogs; caching/coalescing, source-topic reuse and store configuration affect what is logged. Window-store changelogs also use retention policies. On failure or rebalance, a new instance rebuilds the store by replaying the changelog.
- Rebuilding a large store can take minutes, so **standby replicas** (`num.standby.replicas`) keep warm copies on other instances.
- `processing.guarantee=exactly_once_v2` wraps output, changelog writes and offset commits in a Kafka transaction.

| | Flink | Kafka Streams |
|---|---|---|
| Deploy | Cluster (JobManager) | Library in your app |
| Sources | Many | Kafka only |
| State recovery | Checkpoints to S3 | Changelog topics |
| Good for | Large, complex jobs | Kafka-centric services |

## Joins

- **Stream–stream join** (windowed): match clicks with impressions within 30 minutes of each other. Both sides are buffered in state for the window.
- **Stream–table join**: enrich each order with the current customer record. The table is materialised from a compacted topic (a `KTable` in Kafka Streams), so lookups are local, with no remote call per event.
- **Temporal join**: join with the table **as of the event's time**, for example the exchange rate when the payment happened. Flink SQL supports this with versioned tables.

## Worked example: fraud rule

"Alert if a card has purchases in more than 3 distinct countries within 10 minutes."

1. Key the stream by `cardId` so all of a card's events reach one task.
2. Assign event-time timestamps with a 5-second out-of-orderness bound.
3. Buffer events per card until the watermark makes their event-time order eligible for processing. In timestamp order, maintain a rolling 10-minute list of `(time, country)`, evict older entries and count distinct countries. Explicitly send later arrivals beyond the bound to a correction path or discard them under a documented policy.
4. If distinct countries > 3, emit an alert.
5. Register an event-time timer to clear state for idle cards, so state does not grow forever.

An illustrative 200 bytes per card would total 10 GB for 50 million cards before storage overhead. The rolling event list is variable-sized; a reliable capacity estimate is absent because event rate, lateness buffers, indexes, compaction and checkpoint costs were not measured.

## Stream vs batch

A stream processor that can replay a retained log can recompute history, so one codebase can serve both real-time and backfill (the "Kappa architecture"). The architecture module covers batch processing and the trade-offs in more depth.

## Key takeaways
- Stateful operators (aggregations, windows, joins) are the hard part of stream processing; their state must be partitioned by key and recoverable.
- Use event time for meaningful, reproducible results; choose processing time when arrival/wall-clock semantics are intended.
- Tumbling windows do not overlap, hopping windows do, and session windows close after an inactivity gap and can merge.
- Watermarks estimate event-time completeness; they trade latency for completeness, follow the slowest input and need idleness handling.
- Flink checkpoints state together with source offsets; Kafka Streams backs state with compacted changelog topics. Both can provide exactly-once results.

## Further reading
- [Timely stream processing: event time and watermarks (Apache Flink docs)](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/)
- [Windows (Apache Flink docs)](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/operators/windows/)
- [Stateful stream processing (Apache Flink docs)](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/stateful-stream-processing/)
- [Kafka Streams documentation](https://kafka.apache.org/documentation/streams/)
- [The Dataflow Model (Google Research)](https://research.google/pubs/the-dataflow-model-a-practical-approach-to-balancing-correctness-latency-and-cost-in-massive-scale-unbounded-out-of-order-data-processing/)
