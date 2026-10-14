---
id: msg-push-pull-flow-control
title: Push, pull and consumer capacity
level: intermediate
minutes: 2
summary: Choose how messages reach a consumer and how overload signals reach the broker.
sourceLesson: msg-pubsub-fanout
---

The delivery protocol determines who decides when more work arrives. Judge it against processing cost, endpoint reachability and the consumer’s ability to report excess demand.

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

RabbitMQ is a hybrid: the broker pushes over a persistent connection, but **consumer prefetch** acts as a credit limit, so the consumer controls how much is in flight.

> [!tip] Rule of thumb
> Prefer **pull** for high-throughput or heavy processing, where flow control matters. Use **push** for low-volume integrations and serverless endpoints, and make sure the endpoint returns errors quickly when overloaded rather than timing out.

## Key takeaways

- HTTP push needs a reachable endpoint; pull consumers initiate outbound fetches when capacity is available.
- Push endpoints must fail promptly on overload so the broker can back off.
- RabbitMQ pushes over a consumer-opened connection, with prefetch controlling in-flight deliveries.

## Further reading

- [Push subscriptions (Google Cloud Pub/Sub)](https://cloud.google.com/pubsub/docs/push)
- [AMQP 0-9-1 model explained (RabbitMQ)](https://www.rabbitmq.com/tutorials/amqp-concepts)
