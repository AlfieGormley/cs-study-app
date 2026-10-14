---
id: msg-queue-poison-dead-letter
title: Poison messages, receive counts and dead letters
level: basic
minutes: 3
summary: Classify failures, set aside broken messages and keep recoverable outages from exhausting the retry budget.
sourceLesson: msg-message-queues
---

After processing fails, decide whether another attempt can help. A durable queue gives you time to recover, but repeated receives alone do not repair malformed input or an unavailable dependency.

## Poison messages and dead-letter queues

Some messages will never succeed: malformed JSON, a reference to a deleted customer, a bug triggered by one specific input. Without protection, such a **poison message** is retried forever, wasting capacity and, in FIFO queues, blocking later work in its message group when processing preserves order.

The fix is a **dead-letter queue (DLQ)**: after a set number of failed attempts (say 5), move the message aside.

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

- A poison message needs a bounded retry path and an inspected DLQ, rather than endless redelivery.
- Receive limits and visibility delays must accommodate the outages you expect to recover from.
- RabbitMQ quorum delivery limits can drop messages without a dead-letter exchange; SQS FIFO poison work can block its group.
- Queues suit individually retried tasks; retained logs suit replayable streams.

## Further reading

- [Using dead-letter queues in Amazon SQS (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [Quorum queues (RabbitMQ docs)](https://www.rabbitmq.com/docs/quorum-queues)
- [Dead Letter Channel (Enterprise Integration Patterns)](https://www.enterpriseintegrationpatterns.com/patterns/messaging/DeadLetterChannel.html)
