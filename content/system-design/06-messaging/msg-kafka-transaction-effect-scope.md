---
id: msg-kafka-transaction-effect-scope
title: Kafka transactions and exactly-once effect scope
level: advanced
minutes: 4
summary: Make Kafka outputs and progress atomic while handling read isolation, fencing and external sinks.
sourceLesson: msg-delivery-semantics
---

The familiar consume–process–produce loop has two outputs: its records and its progress. Kafka can commit those together, but work performed in another system needs a separate correctness argument.

## Kafka transactions: exactly-once within Kafka

Kafka's exactly-once semantics (EOS) target a specific pattern: **consume from Kafka, process, produce to Kafka** (read-process-write). The goal is that the output records and the consumer's offset commit happen atomically.

```
in-topic ─▶ app ─▶ out-topic
             │
             └─▶ offsets (same txn)
```

The following is a success-path sketch, not a complete runnable client. Configure a stable transactional.id, disable consumer auto-commit, return the next offset per partition from offsetsOf, and use read_committed for transactional inputs. Production code must abort/reseek on recoverable failure and close a fenced producer:

```java
// Fence older producers using this ID.
producer.initTransactions();
while (true) {
  var recs = consumer.poll(ofMillis(100));
  // Couple output records with progress.
  producer.beginTransaction();
  for (var r : recs)
    producer.send(transform(r));
  // offsetsOf returns the next read
  // offsets.
  producer.sendOffsetsToTransaction(
      offsetsOf(recs),
      consumer.groupMetadata());
  // Commit records and offsets atomically.
  producer.commitTransaction();
}
```

How it works underneath:

1. A **transaction coordinator** (a broker) tracks the transaction in an internal `__transaction_state` log.
2. Output records are written to their partitions immediately but marked as part of an open transaction.
3. On commit, the coordinator writes **commit markers** to every partition involved, including `__consumer_offsets`.
4. Consumers with isolation.level=read_committed see non-transactional records and committed transactional records, up to the last stable offset. An earlier open transaction can delay later records. Aborted records are skipped. The Java consumer's default is `read_uncommitted`, so a downstream consumer that does not set this sees aborted output and loses the guarantee.

**Zombie fencing** handles the nasty case of a consumer that pauses (a long GC pause, say), is presumed dead and replaced, then wakes up and tries to write. Each `transactional.id` has a **producer epoch**; `initTransactions()` bumps it, and the broker rejects writes from the older epoch.

Kafka Streams wraps all of this behind one setting: `processing.guarantee=exactly_once_v2`.

### What Kafka EOS does not cover

EOS is atomic only for **Kafka writes and Kafka offsets**. If your processing step also writes to Postgres, calls an API or sends an email, those effects are outside the transaction. An aborted and retried transaction will perform them again. For external sinks you are back to idempotent writes, or storing offsets in the same database transaction as the results:

This is schematic SQL: the ellipses omit the totals schema and aggregation. The ownership/expected-offset guard described below is also required; the sketch alone does not fence a stale consumer.

```sql
BEGIN;
-- Apply the batch to the external result.
INSERT INTO totals ... ON CONFLICT ...;
-- Store where this committed batch ends.
UPDATE kafka_offsets SET next = 1043
 WHERE topic='pay' AND part=3;
-- Result and position move together.
COMMIT;
```

On startup (and after every rebalance) the consumer reads `kafka_offsets` and calls `seek()` to that position instead of trusting `__consumer_offsets`. Results and position then move together. Also enforce ownership or the expected offset atomically in that transaction: after a rebalance, an old consumer can still be running, and storing offsets alone does not fence its writes.

A universal transaction-overhead percentage is absent because no representative benchmark configuration is established here. Transaction commit coordination adds work, and read-committed visibility can add latency. Longer commit intervals mean higher throughput but more latency.

## Choosing in practice

1. Default to **at-least-once** delivery.
2. Make every consumer **idempotent**: natural idempotence first, then dedup tables in the same transaction, then idempotency keys for external calls.
3. Use **Kafka transactions** (or Kafka Streams EOS) for Kafka-to-Kafka pipelines where duplicates in output topics matter, such as financial aggregations.
4. Use **at-most-once** only where loss is acceptable and a duplicate is worse than nothing.

## Key takeaways

- Kafka transactions combine output records and consumed offsets; readers need read_committed to hide aborted output.
- A newer producer epoch fences a paused older producer using the same transactional identity.
- External database/API effects need their own idempotence or atomic results-plus-offsets design with an ownership guard.
- Exactly-once is a boundary to design and test, rather than a promise that covers every side effect.

## Further reading

- [Exactly-once semantics are possible: here's how Kafka does it (Confluent)](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/)
- [Transactions in Apache Kafka (Confluent)](https://www.confluent.io/blog/transactions-apache-kafka/)
- [Kafka message delivery semantics (Confluent docs)](https://docs.confluent.io/kafka/design/delivery-semantics.html)
- [Kafka 4.2 producer API](https://kafka.apache.org/42/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html)
