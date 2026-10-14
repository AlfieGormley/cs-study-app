---
id: msg-subscription-routing-filters
title: Route events with subscription filters
level: intermediate
minutes: 2
summary: Apply SNS filter policies and RabbitMQ topic bindings to deliver only matching events.
sourceLesson: msg-pubsub-fanout
---

A subscription need not receive every published event. Filtering selects the subset before a worker spends time receiving and discarding it. In the policy below, all three listed fields must match; the array for a field lists its accepted alternatives.

## Filtering

Often a subscriber cares about only some messages. Shipping does not need `OrderCancelled` events for digital goods. Rather than receiving everything and discarding most of it, the subscriber can set a **filter policy**.

```json
{
  "eventType": ["OrderPlaced"],
  "fulfilment": ["physical"],
  "amount": [{ "numeric": [">=", 100] }]
}
```

The example accepts physical `OrderPlaced` messages whose numeric `amount` is at least 100; it does not transform the payload.

SNS evaluates filter policies against **message attributes** by default, or against the message body if you set the filter policy scope to `MessageBody`. Messages that do not match are simply not delivered to that subscription.

Filtering saves consumer compute and queue costs, but it moves routing logic into infrastructure configuration. Keep filter policies in version control alongside the consumer's code.

RabbitMQ achieves similar routing with **topic exchanges**: queues bind with patterns such as `order.*.physical` or `order.#`, where `*` matches one word and `#` matches zero or more.

## Key takeaways

- SNS filters use message attributes by default, with an optional message-body scope.
- RabbitMQ topic bindings use a one-word wildcard and a zero-or-more-word wildcard.
- Keep routing configuration versioned with the subscriber so filtering changes can be reviewed.

## Further reading

- [Amazon SNS message filtering (AWS docs)](https://docs.aws.amazon.com/sns/latest/dg/sns-message-filtering.html)
- [AMQP 0-9-1 model explained (RabbitMQ)](https://www.rabbitmq.com/tutorials/amqp-concepts)
