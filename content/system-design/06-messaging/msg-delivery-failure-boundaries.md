---
id: msg-delivery-failure-boundaries
title: Delivery semantics at a failure boundary
level: advanced
minutes: 2
summary: Distinguish possible loss, duplicate delivery and exactly-once effects under explicit assumptions.
sourceLesson: msg-delivery-semantics
---

Every messaging system has to answer one question: if something fails mid-flight, **might a message be lost, duplicated, or neither?** The answer is the system's **delivery semantics**. Getting this right is the difference between a payment taken once and a payment taken twice.

## Why this is hard

Consider a consumer that processes a message and then acknowledges it. There are two failure points:

```
receive ─▶ process ─▶ ack
         ✗1         ✗2
```

- Crash at ✗1 (before processing completes): if the broker already considered the message done, it is **lost**.
- Crash at ✗2 (after processing, before the ack reaches the broker): the broker redelivers, so it is **duplicated**.

The broker cannot tell these apart. It only knows it did not get an ack. Neither can the producer when a publish times out: did the broker store it or not? This is a form of the [Two Generals' Problem](https://en.wikipedia.org/wiki/Two_Generals%27_Problem): over an unreliable network, no finite exchange of messages lets both sides be certain the other knows.

## The three semantics

| Semantics | Loss? | Duplicates? | How |
|---|---|---|---|
| At-most-once | Possible | No | Ack before work |
| At-least-once | No | Possible | Ack after work, retry |
| Exactly-once | No | No | At-least-once + dedup |

These categories describe a defined failure model and processing boundary. Early acknowledgement does not remove duplicates already introduced by producers or an at-least-once broker; retention expiry and permanent failures can defeat eventual processing. Exactly-once effects require atomic effect/dedup state and sufficient retry/dedup retention.

**At-most-once** suits data where loss is tolerable and duplicates are harmful or pointless: metrics sampling, some telemetry, "typing…" indicators.

**At-least-once** is the default for almost everything: SQS, SNS, RabbitMQ with manual acks, Kafka with commit-after-processing.

**Exactly-once** *delivery* across a network is impossible in general. What systems actually provide is **exactly-once processing** (often called *effectively-once*): messages may be delivered more than once, but their **effects** are applied once.

> [!note] The formula
> **Effectively-once = at-least-once delivery + idempotent (or deduplicated) processing.** Every practical exactly-once system, including Kafka's, is built this way.

## Key takeaways

- A missing acknowledgement does not reveal whether the consumer finished its effect.
- Acknowledging before work trades retry duplicates for possible loss under the stated boundary.
- Exactly-once effects require safe duplicate handling, atomic state changes and a sufficient retention horizon.

## Further reading

- [Kafka message delivery semantics (Confluent docs)](https://docs.confluent.io/kafka/design/delivery-semantics.html)
- [Idempotent Receiver (Enterprise Integration Patterns)](https://www.enterpriseintegrationpatterns.com/patterns/messaging/IdempotentReceiver.html)
