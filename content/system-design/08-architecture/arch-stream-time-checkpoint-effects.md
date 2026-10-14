---
id: arch-stream-time-checkpoint-effects
title: Separating stream time and recovered effects
level: advanced
minutes: 3
summary: Choose event-time windows and late-data policies, then distinguish checkpointed state from external sink correctness.
sourceLesson: arch-batch-vs-stream
---

A stream has no natural end at which to run a final batch. This unit defines when results become useful and what recovery must preserve.

## Stream processing

A stream processor runs continuously over an **unbounded** sequence of events, usually read from a log like Kafka, and emits results as events arrive. Examples: Apache Flink, Kafka Streams, Spark Structured Streaming, Google Dataflow (Apache Beam).

Concepts you can't avoid:

- **Event time vs processing time.** A phone records a tap at 12:00:01 (event time) but is offline, so it reaches you at 12:07 (processing time). Aggregating by processing time puts it in the wrong minute.
- **Windowing**: group an infinite stream into finite chunks.
  - *Tumbling window*: fixed, non-overlapping (each minute).
  - *Sliding (hopping) window*: overlapping (last 5 minutes, every 1 minute).
  - *Session windows*: activity separated by gaps of inactivity.
- **Watermarks**: an event-time progress estimate, not a promise that older data cannot arrive. Window triggers and cleanup depend on the engine and allowed-lateness policy; late data can update results, go to a side output or be dropped.
- **State**: counts, joins and windows need state. Flink keeps it locally (often in RocksDB) and periodically takes consistent **checkpoints** to durable storage.
- **Exactly-once** results: Flink can recover internal state consistently using checkpoints and replayable sources. End-to-end effects require a compatible transactional sink or a carefully ordered, versioned idempotent design. An arbitrary external call or plain keyed upsert does not automatically give exactly-once observable behavior.

This recovery diagram is illustrative: the repeated output is correct only with the source and sink protocol just described. It does not promise identical external effects from arbitrary sink calls.

```
 Kafka --> [Flink job]
   |        keyed state per user
 offsets    | checkpoint every 30s
   |        v
   +--- [S3: state + offsets]
 on failure: restore state, rewind
 offsets, reprocess -> same output
```

### Publish corrections deliberately

A ten-minute sliding (hopping) window advancing each minute overlaps neighbouring windows; trigger timing is a separate engine policy. If a late event changes a published total, emit a defined replacement, versioned update or changelog delta. Blindly adding replacement totals double-counts. Checkpoint restoration may replay events whose outputs already reached the sink: increments can double-count, while bare upserts can regress when stale attempts race. Test the sink's commit/abort, ordering and retry protocol; a checkpoint interval alone supplies no external exactly-once guarantee.

## Key takeaways
- Event time records when an event happened; processing time records when the processor observes it.
- Tumbling, sliding and session windows group unbounded input with different overlap and closure rules.
- Watermarks estimate progress; lateness and correction policies decide what happens to older arrivals.
- Consistent checkpoints recover internal state, while external exactly-once effects require a compatible transaction or proven versioned protocol.

## Further reading
- [Apache Flink: Timely stream processing](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/)
