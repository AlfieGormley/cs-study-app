---
id: msg-subscriptions-sns-sqs
title: Independent subscriptions with SNS and SQS
level: intermediate
minutes: 3
summary: Give every reacting service its own durable queue and understand partial subscriber completion.
sourceLesson: msg-pubsub-fanout
---

A queue hands each message to **one** consumer. But many real messages are facts that several systems care about. When an order is placed, billing, shipping, analytics and email all want to know. **Publish/subscribe** (pub/sub) solves this: a publisher sends a message to a **pub/sub topic**, and the broker delivers to each matching subscription according to its delivery guarantees.

## Topics and subscriptions

```
            ┌─▶ sub: billing  ─▶ svc
publisher ─▶│
  (topic)   ├─▶ sub: shipping ─▶ svc
            └─▶ sub: email    ─▶ svc
```

- The **message publisher** knows only the topic name. It has no idea who is listening.
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

Delivery to each subscription is independent. Billing may not have created an invoice when Email starts handling the same `OrderPlaced` event. If Email requires an invoice, trigger it from `InvoiceIssued` or use another explicit readiness protocol rather than assuming Billing runs first.

## Key takeaways

- Pub/sub copies a fact to each matching subscription; workers within one queue compete for its copy.
- SNS-to-SQS fan-out isolates each service’s backlog, retry path and worker capacity.
- Configure the queue access policy and either unwrap the SNS envelope or enable raw delivery.
- Independent subscribers do not complete together: publish or check explicit prerequisites.

## Further reading

- [Fanout Amazon SNS notifications to Amazon SQS queues (AWS docs)](https://docs.aws.amazon.com/sns/latest/dg/sns-sqs-as-subscriber.html)
- [Publish–subscribe pattern (Wikipedia)](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern)
