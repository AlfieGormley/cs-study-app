---
id: msg-stream-joins-keyed-fraud
title: Stream joins and keyed fraud state
level: advanced
minutes: 3
summary: Enrich streams locally, retain historical table versions for replay and bound keyed fraud state.
sourceLesson: msg-stream-processing
---

State is useful both for looking up another stream’s data and for remembering one key’s recent history. The right state model determines runtime coupling, replay correctness and memory requirements.

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

A rough state estimate multiplies the number of keys by the state each one holds:

```formula
M = n × b
M = 50000000 × 200 B = 10 GB
where
M: the total state held across the job
n: the number of cards with state, here 50 million
b: an illustrative state size per card, 200 bytes (B)
B: bytes
GB: gigabytes, billions of bytes
In words: 50 million cards at 200 bytes each is about 10 GB of state, before storage overhead.
```

That figure is only illustrative. The rolling event list is variable-sized; a reliable capacity estimate is absent because event rate, lateness buffers, indexes, compaction and checkpoint costs were not measured.

## Stream vs batch

A stream processor that can replay a retained log can recompute history, so one codebase can serve both real-time and backfill (the "Kappa architecture"). The architecture module covers batch processing and the trade-offs in more depth.

## Key takeaways

- Stream–table enrichment materialises a local lookup instead of making one remote call per event.
- Historical replay needs table versions valid at each event time; a compacted latest-value table alone loses that history.
- Key fraud state by card, process eligible event-time order, evict old entries and remove card data after inactivity.
- The 10 GB illustration excludes variable event lists, indexes, lateness buffers and recovery overhead; measure them.

## Further reading

- [Windows (Apache Flink docs)](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/operators/windows/)
- [Stateful stream processing (Apache Flink docs)](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/stateful-stream-processing/)
- [Kafka Streams documentation](https://kafka.apache.org/documentation/streams/)
- [Flink SQL joins](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/queries/joins/)
