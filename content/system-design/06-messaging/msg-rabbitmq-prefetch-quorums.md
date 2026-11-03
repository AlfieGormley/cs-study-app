---
id: msg-rabbitmq-prefetch-quorums
title: RabbitMQ prefetch and replicated quorum queues
level: basic
minutes: 3
summary: Control unacknowledged deliveries with prefetch and predict how many replica failures a quorum queue survives.
sourceLesson: msg-message-queues
---

RabbitMQ pushes deliveries over an existing connection. The consumer controls its exposure with prefetch, while replicated quorum queues protect the broker-side record of the work.

## How RabbitMQ does it: channels, acks and prefetch

RabbitMQ consumers hold a long-lived TCP connection. The broker *pushes* messages to them, and it knows a consumer has died when the connection or its AMQP channel closes.

- Consumers send `basic.ack` when done, or `basic.nack` / `basic.reject` to give up (optionally with `requeue=true`).
- Unacknowledged messages on a closed channel are **requeued** automatically.
- **Consumer prefetch** (`basic.qos`) limits how many unacknowledged messages a consumer may hold at once.

The prefetch limit is a crucial knob. A prefetch of 0 means unlimited: with a classic queue, the first consumer to connect can be pushed a large share of the backlog as unacknowledged deliveries, leaving little for consumers that join later. (Quorum queues cap prefetch at 2,000, and broker defaults can impose other bounds.) A prefetch of 1 prevents a consumer holding more than one unacknowledged delivery, but it significantly reduces throughput because each consumer waits a network round trip between messages. RabbitMQ's documentation says values from about 100 to 300 usually give near-optimal throughput; lower values share slow jobs more evenly. Measure with your real processing times.

> [!analogy] Real-world analogy: markers sharing a pile of exam scripts
> A pile of exam scripts sits on a table. If there is no rule, the first marker to arrive can take most of the pile back to their desk, and markers who arrive later find almost nothing left. Say "take at most 50 at a time" and everyone gets a share, while each marker still has enough on their desk not to keep walking back to the table.
>
> **How it maps:** The pile is the queue, each marker is a consumer, and the scripts on a desk are unacknowledged deliveries. The "at most 50" rule is the prefetch limit: small enough to share work fairly, large enough to avoid a round trip per message.
>
> **Where it stops:** A marker can hand scripts back whenever they like, but RabbitMQ only returns unacknowledged deliveries to the queue when the consumer rejects them or its channel closes. And RabbitMQ pushes scripts to the desk; consumers do not walk over and fetch them.

Producers publish to a **RabbitMQ exchange**, which routes each message into queues. There are four exchange types: direct exchange, topic exchange, fanout exchange and headers exchange. For durability use **quorum queues**, which replicate each queue across nodes using the Raft consensus algorithm. A write is confirmed once a majority of replicas have it, and the queue keeps working only while a majority is still up. So a 3-replica queue survives one node failure and a 5-replica queue survives two.

```formula reference
f = ⌊(n − 1) / 2⌋
where
f: the number of replicas (nodes) that can fail while the queue still accepts and confirms writes
n: the number of replicas of the queue, usually an odd number such as 3 or 5
⌊ ⌋: floor: round down to the whole number below, so ⌊1.5⌋ = 1
In words: a majority must survive, so a queue can lose just under half its replicas: 3 replicas survive 1 failure, 5 survive 2, and a fourth replica adds no extra tolerance over 3.
```

A 4-replica queue still survives only one failure, because 2 out of 4 is not a majority; that is why replica counts are usually odd. Lose the majority and the queue stops accepting work rather than risk losing confirmed messages. Quorum queues are always durable and cannot be exclusive or transient.

The older alternative, *classic mirrored queues*, was deprecated for years and **removed in RabbitMQ 4.0** (2024). Anything still relying on mirroring must move to quorum queues (or streams) before upgrading.

## Key takeaways

- RabbitMQ requeues unacknowledged deliveries when their channel closes.
- Prefetch limits in-flight work and can prevent an early consumer taking a large backlog; benchmark the setting.
- Quorum queues need a surviving majority, and classic mirroring was removed in RabbitMQ 4.0.

## Further reading

- [RabbitMQ tutorial: work queues, acks and fair dispatch](https://www.rabbitmq.com/tutorials/tutorial-two-python)
- [Quorum queues (RabbitMQ docs)](https://www.rabbitmq.com/docs/quorum-queues)
