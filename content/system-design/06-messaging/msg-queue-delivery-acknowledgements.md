---
id: msg-queue-delivery-acknowledgements
title: Competing consumers and acknowledgement failures
level: basic
minutes: 2
summary: Trace receive, process and acknowledgement to see why a worker crash can cause loss or duplication.
sourceLesson: msg-message-queues
---

A message queue is the simplest broker: producers put messages in, consumers take them out, and **each delivery is assigned to one competing consumer, rather than broadcast to every consumer**. This is called **point-to-point messaging**. It is the workhorse behind background jobs, email sending, image processing and most "do this later" tasks.

## Competing consumers

You scale a queue by running several consumers against it. They **compete** for messages: whichever is free takes the next one.

```
           ┌──▶ worker A
producer ─▶[ m5 m4 m3 m2 m1 ]──▶ worker B
           └──▶ worker C
```

This gives you three properties almost for free:

- **Horizontal scaling.** More workers can increase throughput until queue partitions, broker resources, contention or downstream capacity limit it.
- **Resilience.** If worker B crashes, A and C keep going.
- **Natural load balancing.** A fast worker simply asks for more often.

The catch is **ordering**. With several competing consumers, m2 may finish before m1. If ordering matters, you need FIFO queues with group IDs (covered later in this module) or partitioned processing on a log like Kafka; application concurrency must also preserve the required order.

## The core problem: when is a message "done"?

A consumer can crash halfway through processing. If the broker deleted the message the moment it was handed out, that work would be lost. So brokers separate **delivery** from **completion** using **acknowledgements**.

```
1. receive   broker ──m1──▶ worker
2. process   worker does the work
3. ack       worker ──ack──▶ broker
4. delete    broker removes m1
```

If step 3 never happens, the broker assumes the worker died and **redelivers** the message to someone else. This is what makes queues reliable, and it is also why messages can be **delivered more than once**: a worker might finish step 2, then crash before step 3.

> [!warning] Ack after, not before
> Acknowledging before processing (auto-ack) gives you *at-most-once* delivery: a crash mid-processing loses the message. Acknowledging after processing gives you *at-least-once*: a crash after processing but before the ack means a duplicate. Most systems choose at-least-once and make consumers idempotent.

## Key takeaways

- Consumers share work rather than each receiving a broadcast copy.
- Completion acknowledgements let the broker redeliver unfinished work after a consumer disappears.
- A crash after an effect but before acknowledgement can repeat the effect; consumers must tolerate duplicates.

## Further reading

- [RabbitMQ tutorial: work queues, acks and fair dispatch](https://www.rabbitmq.com/tutorials/tutorial-two-python)
- [Competing Consumers pattern (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/competing-consumers)
