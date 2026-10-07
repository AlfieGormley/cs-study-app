---
id: msg-delivery-semantics
title: Delivery semantics and idempotent consumers
level: advanced
minutes: 14
summary: At-most-once, at-least-once and exactly-once explained honestly, with idempotent consumers, deduplication and how Kafka transactions really work.
---

Every messaging system has to answer one question: if something fails mid-flight, **might a message be lost, duplicated, or neither?** The answer is the system's **delivery semantics**. Getting this right is the difference between a payment taken once and a payment taken twice.

## Why this is hard

Consider a consumer that processes a message and then acknowledges it. There are two failure points:

```
receive ─▶ process ─▶ ack
         ✗1         ✗2
```

- Crash at ✗1 (before processing completes): if the broker already considered the message done, it is **lost**.
- Crash at ✗2 (after processing, before the ack reaches the broker): the broker redelivers, so it is **duplicated**.

The broker cannot tell these apart. It only knows it did not get an ack. Neither can the producer when a publish times out: did the broker store it or not? This is a form of the [Two Generals' Problem](https://en.wikipedia.org/wiki/Two_Generals%27_Problem): over an unreliable network, no finite exchange of messages lets both sides be certain the other knows.

## The three semantics

| Semantics | Loss? | Duplicates? | How |
|---|---|---|---|
| At-most-once | Possible | No | Ack before work |
| At-least-once | No | Possible | Ack after work, retry |
| Exactly-once | No | No | At-least-once + dedup |

These categories describe a defined failure model and processing boundary. Early acknowledgement does not remove duplicates already introduced by producers or an at-least-once broker; retention expiry and permanent failures can defeat eventual processing. Exactly-once effects require atomic effect/dedup state and sufficient retry/dedup retention.

**At-most-once** suits data where loss is tolerable and duplicates are harmful or pointless: metrics sampling, some telemetry, "typing…" indicators.

**At-least-once** is the default for almost everything: SQS, SNS, RabbitMQ with manual acks, Kafka with commit-after-processing.

**Exactly-once** *delivery* across a network is impossible in general. What systems actually provide is **exactly-once processing** (often called *effectively-once*): messages may be delivered more than once, but their **effects** are applied once.

> [!note] The formula
> **Effectively-once = at-least-once delivery + idempotent (or deduplicated) processing.** Every practical exactly-once system, including Kafka's, is built this way.

## Idempotent consumers

An operation is **idempotent** if applying it twice has the same effect as applying it once. Design consumers so a redelivered message does no harm.

### 1. Naturally idempotent operations

Some operations are idempotent by construction:

| Not idempotent | Idempotent |
|---|---|
| `balance += 10` | `SET status='SHIPPED'` |
| `INSERT` new row | `UPSERT` by natural key |
| Send email | Provider-enforced dedup key |

Prefer **absolute state** ("order 17 is shipped") over **deltas** ("add one to shipped count") in message design where you can.

### 2. Deduplication by message ID

When the operation is not naturally idempotent, record which messages you have processed, **in the same transaction as the effect**:

```sql
BEGIN;
INSERT INTO processed_messages(id)
  VALUES ('msg-8f3a'); -- PK: fails if seen
UPDATE accounts SET balance = balance + 10
  WHERE id = 42;
COMMIT;
```

If the message is redelivered, the insert violates the primary key, the transaction rolls back, and the consumer acks the duplicate. Because the dedup record and the effect commit atomically, there is no window where one exists without the other.

> [!warning] Dedup outside the transaction is racy
> "Check Redis for the ID, do the work, then write the ID to Redis" fails two ways: a crash after the work but before the Redis write causes a duplicate, and two consumers receiving the same message concurrently both see "not processed". Use an atomic claim (a unique insert, or Redis `SET key NX`) and make the effect itself safe to retry.

The ID must be stable across retries. Use a producer-assigned ID (an event ID or a business-operation key; orderId + eventType is only sufficient if that event type can occur once per order), **not** the broker's delivery ID, which may change on redelivery.

Keep deduplication state for the full permitted duplicate horizon, including delayed retries, archives and replay duration. Permanent business records may be appropriate when no reliable finite bound exists.

### 3. Idempotency keys for side effects

When the effect is a call to an external system (charging a card, sending an SMS), pass an **idempotency key** derived from the message. Stripe, for example, accepts an `Idempotency-Key` header and returns the original result for a repeated key; it keeps keys for at least 24 hours. The external system does the dedup for you, but only within its own retention window, so a retry after pruning may be a fresh request. If the earlier outcome is uncertain, reconcile it before retrying outside that window.

### 4. Version checks

For state updates, include a version or sequence number and apply only if it is newer:

```sql
UPDATE profiles SET email = :email,
       version = :v
 WHERE id = :id AND version < :v;
```

For absolute state snapshots with a single ordered version domain, this rejects stale updates. It does not safely skip missing deltas; initialise absent rows and coordinate versions across writers.

## Producer-side duplicates

Duplicates also start at the producer. A publish times out, the producer retries, and the broker ends up with two copies.

- **SQS FIFO** deduplicates on `MessageDeduplicationId` (or a SHA-256 of the body with content-based deduplication) for a **5-minute** window.
- **Kafka idempotent producer** (default since 3.0): each producer has a producer ID and a per-partition sequence number. The broker rejects duplicates and out-of-order sequence numbers. This removes retry duplicates **within one producer session**, but a restarted producer gets a new ID.

## Kafka transactions: exactly-once within Kafka

Kafka's exactly-once semantics (EOS) target a specific pattern: **consume from Kafka, process, produce to Kafka** (read-process-write). The goal is that the output records and the consumer's offset commit happen atomically.

```
in-topic ─▶ app ─▶ out-topic
             │
             └─▶ offsets (same txn)
```

The following is a success-path sketch, not a complete runnable client. Configure a stable transactional.id, disable consumer auto-commit, return the next offset per partition from offsetsOf, and use read_committed for transactional inputs. Production code must abort/reseek on recoverable failure and close a fenced producer:

```java
producer.initTransactions();
while (true) {
  var recs = consumer.poll(ofMillis(100));
  producer.beginTransaction();
  for (var r : recs)
    producer.send(transform(r));
  producer.sendOffsetsToTransaction(
      offsetsOf(recs),
      consumer.groupMetadata());
  producer.commitTransaction();
}
```

How it works underneath:

1. A **transaction coordinator** (a broker) tracks the transaction in an internal `__transaction_state` log.
2. Output records are written to their partitions immediately but marked as part of an open transaction.
3. On commit, the coordinator writes **commit markers** to every partition involved, including `__consumer_offsets`.
4. Consumers with isolation.level=read_committed see non-transactional records and committed transactional records, up to the last stable offset. An earlier open transaction can delay later records. Aborted records are skipped. The Java consumer's default is `read_uncommitted`, so a downstream consumer that does not set this sees aborted output and loses the guarantee.

**Zombie fencing** handles the nasty case of a consumer that pauses (a long GC pause, say), is presumed dead and replaced, then wakes up and tries to write. Each `transactional.id` has an **epoch**; `initTransactions()` bumps it, and the broker rejects writes from the older epoch.

Kafka Streams wraps all of this behind one setting: `processing.guarantee=exactly_once_v2`.

### What Kafka EOS does not cover

EOS is atomic only for **Kafka writes and Kafka offsets**. If your processing step also writes to Postgres, calls an API or sends an email, those effects are outside the transaction. An aborted and retried transaction will perform them again. For external sinks you are back to idempotent writes, or storing offsets in the same database transaction as the results:

```sql
BEGIN;
INSERT INTO totals ... ON CONFLICT ...;
UPDATE kafka_offsets SET next = 1043
 WHERE topic='pay' AND part=3;
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
- Brokers cannot distinguish "crashed before work" from "crashed before ack", so you must choose between possible loss and possible duplicates.
- Exactly-once delivery is impossible over a network; exactly-once processing is at-least-once delivery plus idempotent effects.
- Deduplicate with a stable producer-assigned ID recorded in the same transaction as the effect, or use naturally idempotent writes and version checks.
- Kafka's idempotent producer removes retry duplicates; transactions make output records and offset commits atomic, with zombie fencing and read_committed consumers.
- Kafka EOS ends at Kafka's boundary: external side effects still need idempotency.

## Further reading
- [Exactly-once semantics are possible: here's how Kafka does it (Confluent)](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/)
- [Transactions in Apache Kafka (Confluent)](https://www.confluent.io/blog/transactions-apache-kafka/)
- [Kafka message delivery semantics (Confluent docs)](https://docs.confluent.io/kafka/design/delivery-semantics.html)
- [Idempotent Receiver (Enterprise Integration Patterns)](https://www.enterpriseintegrationpatterns.com/patterns/messaging/IdempotentReceiver.html)
- [Making retries safe with idempotent APIs (Amazon Builders' Library)](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
