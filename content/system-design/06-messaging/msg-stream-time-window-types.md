---
id: msg-stream-time-window-types
title: Stream time and window types
level: advanced
minutes: 4
summary: Choose event or processing time, then group records into tumbling, hopping or session windows.
sourceLesson: msg-stream-processing
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
| Ingestion time | When it entered the measured broker or processing system |
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

Use for smoothed moving metrics: "requests in the last 5 minutes, updated every minute". A shorter step at the same window size puts each event in more overlapping windows. A naive implementation updates each window separately, increasing work; incremental aggregation and shared panes can reuse partial results, so actual state and CPU costs depend on the implementation.

Kafka Streams also has a distinct **Kafka Streams sliding window** that is defined by a maximum time difference between records (used for "two events within 10 minutes of each other"), and windows are only created when records arrive.

### Session

Windows defined by **activity gaps** rather than the clock. In event time, a gap between event timestamps (say 30 minutes) separates sessions; watermark progress determines when they fire and are cleaned up. A session can be any length. Sessions for the same key **merge** when a late event bridges them while the necessary state is still retained.

```
user u1: ••• •    ••  •••
         └─s1─┘   └─s2──┘
              ≥30m gap
```

Use for user behaviour analytics: session length, pages per visit.

### Global and count windows

A single window for all time (with custom triggers), or windows of a fixed number of records (say every 100 records). Less common in system design discussions.

## Key takeaways

- Stateful operators depend on earlier records, so their keyed state must survive restart.
- Event time describes when something happened; processing time describes when this run reads it.
- Tumbling windows do not overlap, hopping windows do, and retained sessions can merge when a late event bridges their gap.
- Replay reproducibility needs deterministic inputs and lateness policy as well as event timestamps.

## Further reading

- [Timely stream processing: event time and watermarks (Apache Flink docs)](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/)
- [Windows (Apache Flink docs)](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/operators/windows/)
