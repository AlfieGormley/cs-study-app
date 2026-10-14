---
id: msg-rabbitmq-prefetch-quorums
title: RabbitMQ prefetch and replicated quorum queues
level: basic
minutes: 3
summary: Control unacknowledged deliveries and calculate how many replica failures a quorum queue survives.
sourceLesson: msg-message-queues
---

RabbitMQ pushes deliveries over an existing connection. The consumer controls its exposure with prefetch, while replicated quorum queues protect the broker-side record of the work.

## How RabbitMQ does it: channels, acks and prefetch

RabbitMQ consumers hold a long-lived TCP connection. The broker *pushes* messages to them, and it knows a consumer has died when the connection or its AMQP channel closes.

- Consumers send `basic.ack` when done, or `basic.nack` / `basic.reject` to give up (optionally with `requeue=true`).
- Unacknowledged messages on a closed channel are **requeued** automatically.
- **Consumer prefetch** (`basic.qos`) limits how many unacknowledged messages a consumer may hold at once.

The prefetch limit is a crucial knob. With an unlimited classic-queue prefetch, a consumer can buffer a large backlog before others connect. Broker defaults and quorum-queue limits can impose bounds. A prefetch of 1 prevents a consumer holding multiple unacknowledged deliveries, but is not a perfect fairness guarantee and can reduce throughput. Values between roughly 10 and 300 usually balance throughput and fairness; the right number depends on processing time.

Producers publish to a **RabbitMQ exchange**, which routes each message into queues. There are four exchange types: direct exchange, topic exchange, fanout exchange and headers exchange. For durability use **quorum queues**, which replicate each queue across nodes using the Raft consensus algorithm. A write is confirmed once a majority of replicas have it, and the queue keeps working only while a majority is still up. That fixes how many failures it survives:

```formula
f = ⌊(n − 1) / 2⌋
n = 3: f = ⌊2 / 2⌋ = 1
n = 5: f = ⌊4 / 2⌋ = 2
where
f: the number of replicas (nodes) that can fail while the queue still accepts and confirms writes
n: the number of replicas of the queue, usually an odd number such as 3 or 5
⌊ ⌋: floor: round down to the whole number below, so ⌊1.5⌋ = 1
In words: a majority must survive, so you can lose just under half the replicas: 3 replicas survive 1 failure and 5 survive 2.
```

A 4-replica queue still survives only one failure (⌊3 / 2⌋ = 1), which is why replica counts are usually odd. Lose the majority and the queue stops accepting work rather than risk losing confirmed messages. Quorum queues are always durable and cannot be exclusive or transient.

The older alternative, *classic mirrored queues*, was deprecated for years and **removed in RabbitMQ 4.0** (2024). Anything still relying on mirroring must move to quorum queues (or streams) before upgrading.

## Key takeaways

- RabbitMQ requeues unacknowledged deliveries when their channel closes.
- Prefetch limits in-flight work and can prevent an early consumer taking a large backlog; benchmark the setting.
- Quorum queues need a surviving majority, and classic mirroring was removed in RabbitMQ 4.0.

## Further reading

- [RabbitMQ tutorial: work queues, acks and fair dispatch](https://www.rabbitmq.com/tutorials/tutorial-two-python)
- [Quorum queues (RabbitMQ docs)](https://www.rabbitmq.com/docs/quorum-queues)
