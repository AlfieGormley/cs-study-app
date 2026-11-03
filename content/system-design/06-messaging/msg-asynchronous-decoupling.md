---
id: msg-asynchronous-decoupling
title: What asynchronous messaging decouples
level: basic
minutes: 3
summary: Separate temporal, rate, location and fan-out decoupling without losing sight of the message contract.
sourceLesson: msg-sync-vs-async
---

Asynchronous messaging separates accepting work from finishing it. A queue carries a command to its intended handler; a topic can announce a fact to several independent subscribers.

For example, publishing one `OrderPlaced` event lets email, loyalty and warehouse services subscribe independently. Sending a separate command to every team instead makes the producer maintain that list of handlers. Pub/sub is explored later in the module.

## Asynchronous: send and carry on

In asynchronous communication, the producer hands a **message** to an intermediary (a broker) and can continue after the required broker acknowledgement without waiting for processing. A consumer picks the message up later, maybe milliseconds later, maybe hours.

```
Checkout ─▶ [ queue ] ─▶ Email worker
   │
   └─▶ responds to user at once
```

With durable queues, suitable publish acknowledgement and retention settings, the broker retains the message, so the producer and consumer do not need to be running at the same time. This is the key idea: **the queue decouples the two sides in time**.

> [!analogy] Real-world analogy: the ticket rail in a restaurant kitchen
> A waiter clips an order ticket to the rail and goes back to the tables. Whichever cook is free takes the next ticket. During the lunch rush tickets pile up, and the cooks work through them at their own pace.
>
> **How it maps:** The waiter is the producer, the rail is the broker and the cooks are consumers. The waiter does not wait for the food (asynchronous), does not need a particular cook to be standing there (temporal decoupling), can clip tickets faster than they are cooked (rate decoupling) and never needs to know which cook will take one (location decoupling).
>
> **Where it stops:** A paper ticket can fall off the rail; a broker only keeps a message safe if it is configured to persist and acknowledge it. One ticket goes to one cook, so telling the bar *and* the kitchen needs a copy for each, which is what a topic adds. And the ticket is still a contract: a cook cannot read a ticket written in a new shorthand.

> [!note] Message vs event vs command
> A **command message** asks for something to happen ("SendReceiptEmail"). An **event message** states that something happened ("OrderPlaced"). Both travel as messages. Commands usually have one intended handler; events can have many. You will see why this matters in the pub/sub and event-driven lessons.

## The kinds of decoupling

"Decoupling" gets used loosely. It helps to separate it into distinct properties:

| Kind | What it means |
|---|---|
| Temporal | Consumer can be down when producer sends |
| Rate | Each side runs at its own speed |
| Location | Producer doesn't know consumer's address |
| Fan-out | Add consumers without changing producer |

A direct HTTP request does not by itself buffer work during consumer outages or fan it out; service discovery, proxies and other infrastructure can hide physical consumer addresses. A queue gives you the first three. A publish/subscribe topic adds the fourth.

What a queue does **not** decouple is the **message format**. If the producer changes the shape of the payload, consumers still break. Contracts and schema evolution (for example, Avro or Protobuf with a schema registry) remain your problem.

## Brokers you will meet

- **Amazon SQS, RabbitMQ, Azure Service Bus**: message queues. A message is handed to one consumer and deleted once acknowledged.
- **Amazon SNS, Google Pub/Sub**: publish/subscribe. One message is copied to many subscribers.
- **Apache Kafka, Amazon Kinesis, Redpanda**: distributed logs. Messages are appended and retained; consumers track their own position and can replay.

The next lessons take each family in turn.

## Key takeaways

- Durability, publish acknowledgement and retention let a consumer process work after the producer has moved on.
- Queues decouple time, rate and consumer addresses; pub/sub also lets new subscribers join without changing the producer.
- The payload remains a contract: asynchronous transport does not make incompatible schemas safe.

## Further reading

- [What is a message queue? (AWS)](https://aws.amazon.com/message-queue/)
- [Enterprise Integration Patterns: Messaging](https://www.enterpriseintegrationpatterns.com/patterns/messaging/)
