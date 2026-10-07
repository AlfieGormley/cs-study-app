---
id: msg-message-queues
title: Message queues: competing consumers, acks and DLQs
level: basic
minutes: 13
summary: How point-to-point queues hand each message to one worker, and how acknowledgements, visibility timeouts and dead-letter queues keep work from being lost.
---

A message queue is the simplest broker: producers put messages in, consumers take them out, and **each delivery is assigned to one competing consumer, rather than broadcast to every consumer**. This is called **point-to-point** messaging. It is the workhorse behind background jobs, email sending, image processing and most "do this later" tasks.

## Competing consumers

You scale a queue by running several consumers against it. They **compete** for messages: whichever is free takes the next one.

```
           ┌──▶ worker A
producer ─▶[ m5 m4 m3 m2 m1 ]──▶ worker B
           └──▶ worker C
```

This gives you three properties almost for free:

- **Horizontal scaling.** More workers can increase throughput until queue partitions, broker resources, contention or downstream capacity limit it.
- **Resilience.** If worker B crashes, A and C keep going.
- **Natural load balancing.** A fast worker simply asks for more often.

The catch is **ordering**. With several competing consumers, m2 may finish before m1. If ordering matters, you need FIFO queues with group IDs (covered later in this module) or partitioned processing on a log like Kafka; application concurrency must also preserve the required order.

## The core problem: when is a message "done"?

A consumer can crash halfway through processing. If the broker deleted the message the moment it was handed out, that work would be lost. So brokers separate **delivery** from **completion** using **acknowledgements**.

```
1. receive   broker ──m1──▶ worker
2. process   worker does the work
3. ack       worker ──ack──▶ broker
4. delete    broker removes m1
```

If step 3 never happens, the broker assumes the worker died and **redelivers** the message to someone else. This is what makes queues reliable, and it is also why messages can be **delivered more than once**: a worker might finish step 2, then crash before step 3.

> [!warning] Ack after, not before
> Acknowledging before processing (auto-ack) gives you *at-most-once* delivery: a crash mid-processing loses the message. Acknowledging after processing gives you *at-least-once*: a crash after processing but before the ack means a duplicate. Most systems choose at-least-once and make consumers idempotent.

## How SQS does it: visibility timeouts

Amazon SQS has no persistent connection between broker and consumer, so it cannot notice that a consumer died. Instead it uses a **visibility timeout**.

1. A consumer calls `ReceiveMessage`. SQS returns the message plus a **receipt handle**, and normally hides it from other consumers. Standard queues can still deliver duplicates during the visibility window, so visibility is not an exclusive-processing lock.
2. The message stays invisible for the visibility timeout (default **30 seconds**, maximum **12 hours**).
3. The consumer uses the most recent receipt handle with DeleteMessage after processing. Standard queues can occasionally redeliver even after deletion, and an obsolete receipt handle does not guarantee deletion.
4. If not, the message becomes visible again and another consumer can receive it.

```
t=0     receive m1 (invisible)
t=0–30  worker processing...
t=30    timeout: m1 visible again
t=31    worker B receives m1 (dup!)
```

The key tuning rule: **set the visibility timeout comfortably longer than your worst-case processing time.** AWS suggests at least six times the Lambda function timeout plus any batching window when SQS triggers Lambda. If jobs genuinely vary (a 10-second job sometimes takes 10 minutes), the worker can call `ChangeMessageVisibility` periodically as a heartbeat to extend its lease.

Other SQS details worth knowing:

| Setting | Value |
|---|---|
| Max message size | 1 MiB (256 KB before 2025) |
| Retention | 1 min–14 days (default 4) |
| Long poll wait | up to 20 s |
| Batch receive | up to 10 messages |

For anything bigger than the limit (images, large documents), use the **claim check** pattern: store the payload in S3 and send a small message holding its key. AWS's extended client libraries do this for you.

Use **long polling** (`WaitTimeSeconds=20`). Short polling returns immediately even when the queue is empty, which wastes requests (and money, since SQS bills per request) and can miss messages because it samples only a subset of servers.

Standard SQS queues offer nearly unlimited throughput but only **best-effort ordering** and **at-least-once** delivery. **FIFO queues** guarantee order within a *message group* and deduplicate within a 5-minute window, at lower throughput. Without high-throughput mode, a FIFO queue handles 300 API calls per second per action (`SendMessage`, `ReceiveMessage`, `DeleteMessage`), so up to 3,000 messages per second with batches of 10. **High-throughput mode** spreads groups across internal partitions and raises this to thousands or tens of thousands of calls per second, depending on the region, provided you use many distinct message group IDs.

## How RabbitMQ does it: channels, acks and prefetch

RabbitMQ consumers hold a long-lived TCP connection. The broker *pushes* messages to them, and it knows a consumer has died when the connection or channel closes.

- Consumers send `basic.ack` when done, or `basic.nack` / `basic.reject` to give up (optionally with `requeue=true`).
- Unacknowledged messages on a closed channel are **requeued** automatically.
- **Prefetch** (`basic.qos`) limits how many unacknowledged messages a consumer may hold at once.

Prefetch is a crucial knob. With an unlimited classic-queue prefetch, a consumer can buffer a large backlog before others connect. Broker defaults and quorum-queue limits can impose bounds. A prefetch of 1 prevents a consumer holding multiple unacknowledged deliveries, but is not a perfect fairness guarantee and can reduce throughput. Values between roughly 10 and 300 usually balance throughput and fairness; the right number depends on processing time.

RabbitMQ routes messages via **exchanges** (direct, topic, fanout, headers) into queues. For durability use **quorum queues**, which replicate each queue across nodes using the Raft consensus algorithm. A write is confirmed once a majority of replicas have it, so a 3-replica queue survives one node failure and a 5-replica queue survives two. Lose the majority and the queue stops accepting work rather than risk losing confirmed messages. Quorum queues are always durable and cannot be exclusive or transient.

The older alternative, *classic mirrored queues*, was deprecated for years and **removed in RabbitMQ 4.0** (2024). Anything still relying on mirroring must move to quorum queues (or streams) before upgrading.

## Poison messages and dead-letter queues

Some messages will never succeed: malformed JSON, a reference to a deleted customer, a bug triggered by one specific input. Without protection, such a **poison message** is retried forever, wasting capacity and, in FIFO queues, blocking later work in its message group when processing preserves order.

The fix is a **dead-letter queue (DLQ)**: after N failed attempts, move the message aside.

```
main queue ──fail×5──▶ DLQ
    │                   │
    ▼                   ▼
 workers           alert + inspect
```

- **SQS**: set a *redrive policy* with `maxReceiveCount` (say 5). SQS tracks `ApproximateReceiveCount`; when it exceeds the limit, the message moves to the DLQ. You can later *redrive* messages back to the source queue once the bug is fixed.
- **RabbitMQ**: configure a *dead-letter exchange*. Messages are dead-lettered when rejected without requeue, when their TTL expires, or when the queue exceeds its length limit. Quorum queues also enforce a `delivery-limit`, which **defaults to 20 since RabbitMQ 4.0**: a message redelivered more often than that is dead-lettered if a dead-letter exchange is configured, and **dropped** if not. Exactly which kinds of return count towards the limit has changed between 4.x releases, so check the docs for your version.

> [!tip] A DLQ nobody watches is a black hole
> Always alarm when DLQ depth is above zero, keep DLQ retention longer than the source queue's (otherwise messages can expire before anyone looks), and record *why* a message failed (an error attribute or a log line with the message ID).

## Choosing a receive count

Too low a `maxReceiveCount` (1 or 2) dead-letters messages that hit a transient error, such as a database failover lasting 20 seconds. Too high (100) lets a poison message burn capacity for ages. Three to ten is an illustrative starting range to test against expected outage duration and retry cost, combined with **backoff** between attempts so that transient faults have time to clear.

SQS standard queues have no native per-message backoff, but you can approximate it by calling `ChangeMessageVisibility` on failure with an increasing delay (for example, 30 s, 2 min, 10 min based on the receive count).

## Queue vs log, in one table

| | Queue (SQS, RabbitMQ) | Log (Kafka) |
|---|---|---|
| After ack | Deleted | Retained |
| Unit of scaling | Message | Partition |
| Replay | No | Yes |
| Per-message retry | Easy | Awkward |

Queues shine for **task distribution**: independent jobs where each should be done once and individual failures should be retried or set aside. Logs, covered later, shine for **event streams** that many consumers read and replay.

## Key takeaways
- Point-to-point queues deliver each message to one of many competing consumers, giving easy horizontal scaling but no ordering across workers.
- Acknowledging after processing gives at-least-once delivery; crashes before the ack cause redelivery, so consumers must be idempotent.
- SQS uses visibility timeouts: set them well above worst-case processing time, or extend them with `ChangeMessageVisibility`.
- RabbitMQ pushes to connected consumers; prefetch limits unacked messages and prevents one consumer hogging the queue.
- Dead-letter queues stop poison messages from retrying forever; alarm on them and keep their retention long.

## Further reading
- [Amazon SQS visibility timeout (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)
- [Using dead-letter queues in Amazon SQS (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [Amazon SQS message quotas (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/quotas-messages.html)
- [RabbitMQ tutorial: work queues, acks and fair dispatch](https://www.rabbitmq.com/tutorials/tutorial-two-python)
- [Quorum queues (RabbitMQ docs)](https://www.rabbitmq.com/docs/quorum-queues)
- [Dead Letter Channel (Enterprise Integration Patterns)](https://www.enterpriseintegrationpatterns.com/patterns/messaging/DeadLetterChannel.html)
- [Competing Consumers pattern (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/competing-consumers)
