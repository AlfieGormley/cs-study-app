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

Ordering has a cost: if one message cannot be processed, everything behind it in that lane must wait. In a queue with per-message acks this rarely matters; you just retry that one message. A Kafka consumer can process ahead, but cannot safely advance a contiguous completed-offset checkpoint past failed offset 500 without an explicit recovery design.

A **poison message** is one that will never succeed: bad schema, a bug, missing reference data. Retrying it forever stalls the partition and lag grows without limit.

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

Traditional Kafka consumer groups have no per-record broker acknowledgement/retry; share groups and framework facilities differ, so teams build one. The pattern Uber described for its reprocessing pipeline is widely copied:

```
main ─fail─▶ retry-1m ─fail─▶ retry-10m
                                 │fail
                                 ▼
                                DLQ
```

1. On failure, the consumer publishes the record to `retry-1m` (with an attempt count, original timestamp and retry-eligible time in headers) and commits the original offset atomically with the retry publication using Kafka transactions, or makes retries idempotent and never commits before durable publication. The main partition can then continue.
2. A retry consumer reads `retry-1m`, waits until its retry-eligible time (based on when that retry was scheduled), then tries again.
3. After the final retry tier, the record goes to the **dead-letter topic** for humans.

This trades ordering for throughput: a later event for the same key can overtake the one sitting in a retry tier. That is fine for independent events like "send receipt". It is **not** fine for state transitions like `Created → Updated → Deleted`.

### Parking a key

When ordering per key matters, a better strategy is to **park the key**: when a record fails, send it to a retry/DLQ topic *and* remember that its key is blocked. Every subsequent record for that key is also diverted until the blocked record is resolved. Other keys keep flowing. Preserving order requires durable ordered parking, atomic checkpoint/forwarding coordination and a controlled unpark/drain process; an in-memory blocked flag alone is insufficient.

> [!tip] Separate transient from permanent failures
> A timeout calling a dependency is a **transient failure**: retry with backoff. A JSON parse error is a **permanent failure**: send straight to the DLQ, since retrying wastes time. Classify exceptions explicitly rather than retrying everything the same way.

## Key takeaways

- A failed offset prevents a contiguous completed-progress checkpoint from advancing safely.
- Retry topics restore main-stream flow but let later records overtake the failed record.
- Durable ordered key parking can preserve per-key order while other keys proceed.
- Retry transient failures with delay; permanently malformed input needs a repair/dead-letter path.

## Further reading

- [Error handling patterns in Kafka (Confluent)](https://www.confluent.io/blog/error-handling-patterns-in-kafka/)
