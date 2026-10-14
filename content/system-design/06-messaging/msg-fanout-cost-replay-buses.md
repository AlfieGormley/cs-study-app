---
id: msg-fanout-cost-replay-buses
title: Fan-out costs, replay and event buses
level: intermediate
minutes: 3
summary: Calculate subscriber traffic and distinguish copied queues from retained logs and routed event buses.
sourceLesson: msg-pubsub-fanout
---

Adding subscribers changes cost and recovery options. Queue copies isolate processing, while a retained log lets each group remember its own reading position without a separate stored copy.

## Delivery to many: what can go wrong

Fan-out multiplies messages and therefore multiplies costs and failure modes.

- **Cost.** One publish to a topic with 8 SQS subscriptions is 1 SNS publish plus 8 deliveries, then 8 receives and 8 deletes. At 5,000 orders per second that is 80,000 consumer receive/delete SQS API calls per second (worked out below; fewer with batching).
- **Partial failure.** Delivery to each subscription is independent. Billing may have processed an order that email has not even received yet. Never assume all subscribers are in the same state.
- **Duplicates.** SNS standard topics and SQS standard queues are both at-least-once. Every subscriber must deduplicate independently.
- **Ordering.** Standard SNS gives no ordering guarantee across messages.
- **Slow subscriber.** In a queue-per-subscriber design, one slow consumer's backlog is isolated. In a design where the broker must keep each message until every subscriber has acknowledged it, a slow subscriber can increase storage for everyone.

The cost grows with both the publish rate and the number of subscriptions, because every subscription's consumers must receive, then delete, their own copy of each message:

```formula
R = 2 × λ × k / b
R = 2 × 5000/s × 8 / 1
R = 80000 calls/s
where
R: SQS API calls per second on the consumer side (receives plus deletes)
2: one ReceiveMessage call and one DeleteMessage call per message
λ: lambda, messages published to the topic per second, here 5,000 orders per second
k: the number of SQS queue subscriptions, here 8
b: messages handled per API call (the batch size), 1 without batching and up to 10 with it
calls: API requests, each billed by SQS
s: seconds; "/s" means per second
In words: fan-out multiplies consumer traffic by the number of subscriptions; batching divides it by the batch size.
```

With full batches of 10 the same traffic needs 8,000 calls per second. Real batches are often only partly full at low traffic, so measure the average batch size before relying on that figure.

## Pub/sub on a log

Kafka implements pub/sub differently. There is no copying: a topic is a set of replicated partition logs, and each consumer group tracks an offset per partition. Adding a new group costs almost nothing extra in storage, and a new group can start from the beginning to process history. The next lesson goes deep on this.

| | SNS + SQS | Kafka |
|---|---|---|
| Copies per sub | One per queue | None (offsets) |
| New sub sees past | Standard fan-out: no; optional SNS FIFO archive/replay differs | Yes, within retention |
| Per-message DLQ | Built in | DIY |

## Event bus services

Managed **event buses** such as Amazon EventBridge add content-based routing rules, schema discovery and many built-in targets on top of pub/sub. They are convenient for integrating many services with moderate volume. For very high throughput or replay-heavy workloads, a log such as Kafka or Kinesis is usually a better fit.

## Key takeaways

- Fan-out multiplies receive/delete traffic by subscriber count; effective batching reduces calls.
- Standard SNS/SQS subscribers must handle duplicates and independent ordering or completion.
- A new standard fan-out subscription gets future deliveries; log consumers can replay retained history.
- Event buses help route integrations, while logs fit high-volume replay-heavy streams.

## Further reading

- [Fanout Amazon SNS notifications to Amazon SQS queues (AWS docs)](https://docs.aws.amazon.com/sns/latest/dg/sns-sqs-as-subscriber.html)
- [Publish–subscribe pattern (Wikipedia)](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern)
