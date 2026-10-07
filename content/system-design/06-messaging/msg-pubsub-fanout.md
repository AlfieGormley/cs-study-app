---
id: msg-pubsub-fanout
title: Publish/subscribe and fan-out
level: intermediate
minutes: 10
summary: Topics and subscriptions, the SNS-to-SQS fan-out pattern, message filtering, and when consumers should be pushed messages or pull them.
---

A queue hands each message to **one** consumer. But many real messages are facts that several systems care about. When an order is placed, billing, shipping, analytics and email all want to know. **Publish/subscribe** (pub/sub) solves this: a publisher sends a message to a **topic**, and the broker delivers to each matching subscription according to its delivery guarantees.

## Topics and subscriptions

```
            ┌─▶ sub: billing  ─▶ svc
publisher ─▶│
  (topic)   ├─▶ sub: shipping ─▶ svc
            └─▶ sub: email    ─▶ svc
```

- The **publisher** knows only the topic name. It has no idea who is listening.
- Each **subscription** is an independent stream of copies with its own delivery state.
- Adding a new consumer means adding a subscription. The publisher does not change or redeploy.

This is the fan-out decoupling from the first lesson: the producer is decoupled from the **number and identity** of consumers.

> [!note] Subscription vs consumer
> In most systems a subscription can itself have several consumers competing for its messages. Google Pub/Sub, Azure Service Bus topics and Kafka consumer groups all work this way: **pub/sub between subscriptions, competing consumers within one**.

## The SNS + SQS fan-out pattern

On AWS, SNS is the topic and SQS queues are the subscriptions. This combination is so common that it has a name: **fan-out**.

```
OrderService
     │ publish
     ▼
 [SNS topic: orders]
  │        │        │
  ▼        ▼        ▼
[SQS]    [SQS]    [SQS]
billing  shipping  email
  │        │        │
 workers  workers  workers
```

Why not have each service subscribe to SNS directly over HTTP? Because the queue in between gives each consumer:

- **Durability while it is down.** SNS retries HTTP endpoints for a while, but an SQS queue holds messages for up to 14 days.
- **Its own pace.** Shipping can lag by an hour without affecting billing.
- **Its own retries and DLQ.** A poison message for email does not affect shipping.
- **Independent scaling.** Each queue has its own worker fleet.

Two configuration details trip people up:

1. The SQS queue's **access policy** must allow the SNS topic to send to it.
2. Enable **raw message delivery** if you want the SQS body to be your original payload. Otherwise SNS wraps it in a JSON envelope (`Type`, `MessageId`, `TopicArn`, `Message`...), and your consumer must unwrap it.

SNS FIFO topics can fan out to SQS FIFO queues when ordering within a message group matters.

## Filtering

Often a subscriber cares about only some messages. Shipping does not need `OrderCancelled` events for digital goods. Rather than receiving everything and discarding most of it, the subscriber can set a **filter policy**.

```json
{
  "eventType": ["OrderPlaced"],
  "fulfilment": ["physical"],
  "amount": [{ "numeric": [">=", 100] }]
}
```

SNS evaluates filter policies against **message attributes** by default, or against the message body if you set the filter policy scope to `MessageBody`. Messages that do not match are simply not delivered to that subscription.

Filtering saves consumer compute and queue costs, but it moves routing logic into infrastructure configuration. Keep filter policies in version control alongside the consumer's code.

RabbitMQ achieves similar routing with **topic exchanges**: queues bind with patterns such as `order.*.physical` or `order.#`, where `*` matches one word and `#` matches zero or more.

## Push vs pull consumers

For HTTP push versus polling pull, how does a message reach the consumer? A broker may also push over a connection the consumer originally opened, as RabbitMQ does.

| | Push | Pull |
|---|---|---|
| Who starts | Broker calls you | You ask broker |
| Flow control | Broker guesses | Consumer decides |
| Endpoint | Must be reachable | Can be private |
| Examples | SNS→HTTP, Pub/Sub push | SQS, Kafka |

**Push** delivery (SNS to an HTTPS endpoint, Google Pub/Sub push subscriptions, webhooks) is convenient for serverless handlers: you just expose an endpoint. But the broker controls the rate. If your endpoint slows down, the broker must infer overload from errors or latency and back off. Google Pub/Sub push, for example, uses a slow-start algorithm and reduces its sending rate when it sees failures.

**Pull** delivery (SQS, Kafka, Pub/Sub pull, Kinesis) lets the consumer ask only when it has capacity. This gives natural **backpressure**: a slow consumer simply asks less often, and the backlog builds in the broker, subject to retention, capacity and durability limits. Pull also works for consumers behind firewalls, since they make outbound connections only.

RabbitMQ is a hybrid: the broker pushes over a persistent connection, but **prefetch** acts as a credit limit, so the consumer controls how much is in flight.

> [!tip] Rule of thumb
> Prefer **pull** for high-throughput or heavy processing, where flow control matters. Use **push** for low-volume integrations and serverless endpoints, and make sure the endpoint returns errors quickly when overloaded rather than timing out.

## Delivery to many: what can go wrong

Fan-out multiplies messages and therefore multiplies costs and failure modes.

- **Cost.** One publish to a topic with 8 SQS subscriptions is 1 SNS publish plus 8 deliveries, then 8 receives and 8 deletes. At 5,000 orders per second that is 80,000 consumer receive/delete SQS API calls per second (fewer with batching).
- **Partial failure.** Delivery to each subscription is independent. Billing may have processed an order that email has not even received yet. Never assume all subscribers are in the same state.
- **Duplicates.** SNS standard topics and SQS standard queues are both at-least-once. Every subscriber must deduplicate independently.
- **Ordering.** Standard SNS gives no ordering guarantee across messages.
- **Slow subscriber.** In a queue-per-subscriber design, one slow consumer's backlog is isolated. In a design where the broker must keep each message until every subscriber has acknowledged it, a slow subscriber can increase storage for everyone.

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
- Pub/sub delivers each message to matching subscriptions according to its guarantees; within a subscription, consumers usually compete.
- The SNS + SQS fan-out pattern gives each subscriber durability, its own pace, its own DLQ and independent scaling.
- Filter policies and topic exchanges route only relevant messages to each subscriber.
- Pull consumers get natural backpressure; push delivery is convenient but the broker has to infer the consumer's capacity.
- Fan-out multiplies cost, duplicates and partial-failure states: every subscriber must be idempotent and independent.

## Further reading
- [Fanout Amazon SNS notifications to Amazon SQS queues (AWS docs)](https://docs.aws.amazon.com/sns/latest/dg/sns-sqs-as-subscriber.html)
- [Amazon SNS message filtering (AWS docs)](https://docs.aws.amazon.com/sns/latest/dg/sns-message-filtering.html)
- [Push subscriptions (Google Cloud Pub/Sub)](https://cloud.google.com/pubsub/docs/push)
- [AMQP 0-9-1 model explained (RabbitMQ)](https://www.rabbitmq.com/tutorials/amqp-concepts)
- [Publish–subscribe pattern (Wikipedia)](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern)
