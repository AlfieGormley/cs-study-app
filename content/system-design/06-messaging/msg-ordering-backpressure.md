---
id: msg-ordering-backpressure
title: Ordering, retries, backpressure and lag
level: advanced
minutes: 13
summary: How to keep per-entity ordering without killing parallelism, handle poison messages in ordered streams, and stop a slow consumer from sinking the system.
---

Two problems dominate real messaging systems once they are past the prototype stage. First, **ordering**: some messages must be applied in sequence, yet you want hundreds of consumers in parallel. Second, **flow control**: producers and consumers run at different speeds, and something has to give. This lesson covers both, plus the operational signal that ties them together: **consumer lag**.

## How much ordering do you need?

Global ordering (every message in one sequence) requires a common sequencing/coordination point, though ordered execution and replication can still use multiple machines. That rarely scales. Almost every real requirement is **per-entity ordering**: events for one account, one order, or one device must be in order, but events for different entities are independent.

```
acct A: open ─▶ deposit ─▶ close
acct B: open ─▶ withdraw
  (A and B may interleave freely)
```

The tool for this is a **partition key** (Kafka, Kinesis) or a **message group ID** (SQS FIFO, Azure Service Bus sessions). All messages with the same key go to the same ordered lane, and different keys spread across lanes.

| System | Ordered unit | Parallelism |
|---|---|---|
| Kafka | Partition | Partitions per group |
| Kinesis | Shard | Shards |
| SQS FIFO | Message group | Number of groups |
| Service Bus | Session | Number of sessions |

For sustained provisioned-shard sizing without record aggregation, a Kinesis shard supports 1 MB/s **or** 1,000 records per second of writes, whichever comes first, and shared GetRecords reads have a 2 MB/s shard limit (enhanced fan-out has per-consumer capacity), so you size shards on both bytes and record count and take the larger answer:

```formula
S = ⌈max(W / 1 MB/s, R / 1000/s)⌉
S = ⌈max(2 MB/s / 1 MB/s, 4000/s / 1000/s)⌉
S = ⌈max(2, 4)⌉ = 4
where
S: the minimum number of shards
⌈ ⌉: ceiling: round up to the next whole number, because you cannot have part of a shard
max: the larger of the values inside the brackets
W: the bytes written per second, here 4,000 records of 500 bytes, which is 2 MB/s
R: the records written per second, here 4,000
MB: megabytes; "MB/s" means megabytes per second
s: seconds; "/s" means per second
In words: work out how many shards the byte rate needs and how many the record rate needs, and provision the larger number.
```

Small records hit the record limit first and large records hit the byte limit first. Both limits apply to each shard, so a hot partition key can overload one shard even when the stream's average is fine.

SQS FIFO is notable: it does not lock a whole partition. A single receive can return multiple messages in group order-17; additional receives for that group wait until the in-flight messages are deleted or visible again, but any other group can be served. So parallelism scales with the number of **active groups**, not a fixed partition count.

## Hot keys and skew

Hashing spreads keys evenly only if traffic per key is even. It rarely is. If one celebrity account produces 30% of events, the partition holding that key gets 30% of the load, and its consumer becomes the bottleneck no matter how many others you add.

Mitigations:

- **Pick a finer key.** Order by `conversationId` rather than `userId` if that is what ordering really needs.
- **Salt the hot key.** Spread `celebrity-1` across `celebrity-1#0`…`#7`, accepting that ordering is now only within each sub-key, and merge downstream.
- **Separate topic.** Route known heavy hitters to a dedicated, bigger pipeline.

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

## Consumer lag

**Consumer lag** is how far a consumer group is behind the head of the log. In Kafka it is measured per partition, as a distance in offsets:

```formula
lag = LEO − C
lag = 1500 − 1200 = 300
where
lag: the consumer lag of one partition, in offsets (roughly, records not yet consumed)
LEO: the log end offset: the offset the next record appended to the partition will get
C: the group's committed offset for that partition: the next offset it will read
In words: lag is how many offsets lie between where the group will read next and the end of the log.
```

Offset-distance lag is easy to get but can include compacted gaps or transaction/control offsets; it is not always a count of application records. It is also hard to interpret: 50,000 records is nothing on a topic doing 100,000 per second and alarming on one doing 10 per second. Convert it to **time**, in one of two ways:

- Divide lag by the recent incoming rate (the formula below). This works when the arrival rate is reasonably steady; it is not a reliable instantaneous application of Little's Law during bursts.
- Subtract the timestamp of the record at the committed offset from the current time.

```formula
t_lag ≈ lag / λ
t_lag ≈ 180000 / 2000/s = 90 s
where
t_lag: the approximate age of the backlog: how far behind real time the group is, in seconds (s)
lag: the consumer lag, here 180,000 records
λ: lambda, the recent rate at which records arrive, here 2,000 per second
≈: approximately equal to
s: seconds; "/s" means per second
In words: 180,000 records behind at 2,000 a second is about 90 seconds of traffic behind.
```

Also watch the **trend**. Lag that spikes and recovers is load levelling working. Lag that grows steadily means consumption is slower than production, and it will not recover by itself.

```
lag
 │      ╱╲            ╱
 │     ╱  ╲         ╱
 │ ___╱    ╲____  ╱   ← growing:
 └─────────────────▶     act now
   burst, recovers
```

Tools such as Burrow (from LinkedIn) evaluate lag trends per partition rather than using a fixed threshold. Autoscalers such as KEDA can add consumers based on lag, up to the partition count.

### Diagnosing growing lag

1. **Is it all partitions or one?** One hot partition suggests key skew or a poison message. All partitions suggests too little capacity.
2. **Is the consumer busy or waiting?** High CPU means scale out or optimise. Low CPU with high latency means a slow dependency (database, API).
3. **Is it rebalancing?** Frequent rebalances (check logs for revoked partitions) stall consumption. Common causes are processing exceeding `max.poll.interval.ms`, or deploys without static membership.
4. **Did production rate change?** A new producer or a backfill can double input.

## Retry storms and backoff

When a dependency fails, every consumer retrying immediately multiplies load on it exactly when it is weakest. Use **exponential backoff with jitter**: double the delay after each failed attempt, cap it, then randomise it so clients spread out instead of retrying in lockstep. The "full jitter" form that AWS describes is:

```formula
d_n = min(cap, b × 2^(n − 1))
d_3 = min(60 s, 1 s × 2^2) = 4 s
w_n = random(0, d_n)
where
d_n: the backoff limit before retry number n, in seconds (s)
n: the retry number: 1 for the first retry, 2 for the second, and so on
d_3: the backoff limit before the third retry
min: the smaller of the two values
cap: the largest delay you allow, here 60 s
b: the base delay, here 1 s
^: to the power of; 2^2 = 4
w_n: the time the client actually waits before retry n
random: a number drawn uniformly at random between the two values given
s: seconds
In words: the delays go 1 s, 2 s, 4 s and so on up to the cap, and each client waits a random time up to that delay, so retries spread out instead of arriving together.
```

AWS's article writes the exponent as the attempt count; here n counts retries from 1, so the exponent is n − 1 and the first retry waits up to one base delay. Either way the shape is the same. Then cap the number of attempts, and consider a **circuit breaker** that pauses consumption entirely while the dependency is unhealthy. Pausing is fine for a log; the data waits subject to broker capacity and retention; prolonged pauses can lose access to expired data.

## Key takeaways
- Most systems need per-entity ordering, achieved with partition keys or message group IDs; parallelism then comes from the number of keys or partitions.
- Hot keys cause skew that adding consumers cannot fix; use finer keys, salting or dedicated pipelines.
- In ordered logs a poison message blocks its partition; retry and dead-letter topics restore flow at the cost of per-key order, while parking the key preserves it.
- Backpressure needs bounded buffers at every layer; pull consumers, pause/resume, producer buffer limits and request(n) are concrete mechanisms.
- Monitor consumer lag in time and by trend; growing lag means capacity, skew, poison messages, slow dependencies or rebalances.

## Further reading
- [Error handling patterns in Kafka (Confluent)](https://www.confluent.io/blog/error-handling-patterns-in-kafka/)
- [Burrow: Kafka consumer lag checking (LinkedIn, GitHub)](https://github.com/linkedin/Burrow)
- [Amazon SQS FIFO queues (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues.html)
- [Kafka consumer (Confluent docs)](https://docs.confluent.io/platform/current/clients/consumer.html)
- [Reactive Streams specification](https://www.reactive-streams.org/)
- [Timeouts, retries and backoff with jitter (Amazon Builders' Library)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
