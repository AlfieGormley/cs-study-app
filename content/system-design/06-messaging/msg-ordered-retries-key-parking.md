---
id: msg-ordered-retries-key-parking
title: Ordered retries and parking a failed key
level: advanced
minutes: 3
summary: Choose between blocking, retry topics and durable per-key parking when a record fails.
sourceLesson: msg-ordering-backpressure
---

A retry policy is also an ordering policy. Before moving a failed record aside, decide what must happen to the later records for the same entity.

## Head-of-line blocking and poison messages

Ordering has a cost: if one message cannot be processed, later messages in the same required order must wait. Per-message acknowledgements let a queue track individual completions, but retrying one message can still break entity ordering. A Kafka consumer can process ahead, but cannot safely advance a contiguous completed-offset checkpoint past failed offset 500 without an explicit recovery design.

A **poison message** repeatedly fails under the current processing rules, such as malformed input or a record that triggers a consumer bug. It needs repair or a different handling path. Missing reference data may instead arrive later and permit a retry. Retrying a persistent failure indefinitely stalls that partition's progress; with continuing arrivals, lag grows until retention or another limit intervenes.

```
P3: [498][499][500☠][501][502]...
              ▲ retrying forever
```

You have to choose what to give up:

| Strategy | Keeps order? | Keeps flowing? |
|---|---|---|
| Retry forever | Yes | No |
| Skip to DLQ | No (for that key) | Yes |
| Park key | Yes per key | Yes for others |

### Retry topics and dead-letter topics

Traditional Kafka consumer groups track committed offsets rather than individual broker acknowledgements; share groups and framework facilities differ. A retry-topic design can move failed records through delay tiers like these illustrative one-minute and ten-minute stages:

```
main ─fail─▶ retry-1m ─fail─▶ retry-10m
                                 │fail
                                 ▼
                                DLQ
```

1. On failure, the consumer publishes the record to `retry-1m` (with an attempt count, original timestamp and retry-eligible time in headers) and commits the original offset atomically with the retry publication using Kafka transactions. Downstream consumers must use `read_committed` for the transactional guarantee. Alternatively, tolerate duplicate publication through idempotent retry handling and never commit before durable publication. The main partition can then continue.
2. A retry consumer reads `retry-1m`, waits until its retry-eligible time (based on when that retry was scheduled), then tries again.
3. After the final retry tier, the record goes to the **dead-letter topic** for humans.

This trades ordering for throughput: a later event for the same key can overtake the one sitting in a retry tier. That is fine for independent events like "send receipt". It is **not** fine for state transitions like `Created → Updated → Deleted`.

### Parking a key

When ordering per key matters, a better strategy is to **park the key**: when a record fails, send it to a retry/DLQ topic *and* remember that its key is blocked. Every subsequent record for that key is also diverted until the blocked record is resolved. Other keys keep flowing. Preserving order requires durable ordered parking, atomic checkpoint/forwarding coordination and a controlled unpark/drain process; an in-memory blocked flag alone is insufficient.

> [!tip] Separate transient from permanent failures
> A timeout leaves the call's outcome uncertain; its cause may clear or persist. Retry only when repeating the operation is safe, with bounded attempts, backoff and an overall deadline. An unchanged malformed JSON payload will not become valid merely by waiting: quarantine it with diagnostic context for repair. Classify the cause and service contract, not just an exception name. During sustained dependency failure, explicitly pause affected consumption while maintaining required polling, and monitor retention and backlog; a circuit breaker alone does not pause a Kafka consumer.

## Key takeaways

- A failed offset prevents a contiguous completed-progress checkpoint from advancing safely.
- Retry topics restore main-stream flow but let later records overtake the failed record.
- Durable ordered key parking can preserve per-key order while other keys proceed.
- Retry transient failures with delay; permanently malformed input needs a repair/dead-letter path.

## Further reading

- [Error handling patterns in Kafka (Confluent)](https://www.confluent.io/blog/error-handling-patterns-in-kafka/)
- [Transient fault handling (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/best-practices/transient-faults)
- [Kafka consumer API](https://kafka.apache.org/42/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html)
- [Kafka producer API and transactions](https://kafka.apache.org/42/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html)
