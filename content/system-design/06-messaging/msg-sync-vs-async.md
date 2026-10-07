---
id: msg-sync-vs-async
title: Synchronous vs asynchronous communication
level: basic
minutes: 9
summary: Why systems put a queue between services, what decoupling really buys you, and how a queue absorbs traffic spikes.
---

When one service needs another to do something, it has two basic choices. It can **ask and wait** (synchronous), or it can **leave a note and move on** (asynchronous). Almost every messaging system you will meet in this module exists to make the second option reliable.

## Synchronous: request and wait

In a synchronous call, the caller sends a request (usually HTTP or gRPC) and logically waits for a response or timeout; a nonblocking client need not block an operating-system thread.

```
Checkout ──HTTP──▶ Payments ──▶ Fraud
   ▲                  │            │
   └──── waits ───────┴── waits ───┘
```

This is simple and gives you an immediate answer, which is exactly what you want when the user is waiting for that answer: "was my card accepted?"

But synchronous chains have three structural weaknesses:

- **Availability multiplies.** If Checkout requires three services that are each 99.9% available and their failures are independent, dependency availability is 0.999³ ≈ 99.7%. Correlated failures change this calculation, and Checkout has its own failure modes. That is about 26 hours of downtime a year instead of 8.8.
- **Latency adds up.** Sequential dependent calls add their durations; parallel fan-out waits for the required critical path, and tail latency (p99) gets worse as you add hops, because the slowest dependency dominates. If a request touches 5 services with independent delays and each is slow 1% of the time, the request hits at least one slow call 1 − 0.99⁵ ≈ 4.9% of the time: tail slowness becomes more frequent at the request level; exact quantiles depend on the full latency distributions.
- **Load is coupled.** A spike at the front door hits every downstream service at the same instant. If Fraud can only handle 500 requests a second, Checkout can only handle 500 requests a second.

## Asynchronous: send and carry on

In asynchronous communication, the producer hands a **message** to an intermediary (a broker) and can continue after the required broker acknowledgement without waiting for processing. A consumer picks the message up later, maybe milliseconds later, maybe hours.

```
Checkout ─▶ [ queue ] ─▶ Email worker
   │
   └─▶ responds to user at once
```

With durable queues, suitable publish acknowledgement and retention settings, the broker retains the message, so the producer and consumer do not need to be running at the same time. This is the key idea: **the queue decouples the two sides in time**.

> [!note] Message vs event vs command
> A **command** asks for something to happen ("SendReceiptEmail"). An **event** states that something happened ("OrderPlaced"). Both travel as messages. Commands usually have one intended handler; events can have many. You will see why this matters in the pub/sub and event-driven lessons.

## The kinds of decoupling

"Decoupling" gets used loosely. It helps to separate it into distinct properties:

| Kind | What it means |
|---|---|
| Temporal | Consumer can be down when producer sends |
| Rate | Each side runs at its own speed |
| Location | Producer doesn't know consumer's address |
| Fan-out | Add consumers without changing producer |

A direct HTTP request does not by itself buffer work during consumer outages or fan it out; discovery, proxies and other infrastructure can hide physical consumer addresses. A queue gives you the first three. A publish/subscribe topic adds the fourth.

What a queue does **not** decouple is the **message format**. If the producer changes the shape of the payload, consumers still break. Contracts and schema evolution (for example, Avro or Protobuf with a schema registry) remain your problem.

## Load levelling

The most common practical reason to add a queue is to protect a slow or fragile component from bursts. This is the **queue-based load levelling** pattern.

Imagine an image-thumbnail service. Uploads arrive in bursts: 2,000 per second for 30 seconds after a marketing email, then 50 per second for the rest of the hour. Each worker can process 100 images per second.

```
 arrivals/s
 2000 ┤ ████
      │ ████
      │ ████
  200 ┤ ████ - - - - - - - - - workers
   50 ┤ ████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
      └──────────────────────▶ time
```

Without a queue, you need 20 workers (2,000 ÷ 100) sitting mostly idle to survive the peak. With a queue and 2 workers (200 per second capacity):

1. During the burst, the backlog grows at 2,000 − 200 = 1,800 messages per second.
2. After 30 seconds the backlog is 1,800 × 30 = 54,000 messages.
3. Afterwards, arrivals drop to 50 per second, so the backlog drains at 200 − 50 = 150 per second.
4. Draining takes 54,000 ÷ 150 = 360 seconds, or 6 minutes.

So you trade **latency** (the largest FIFO waiting time is about 54,000 ÷ 200 = 270 seconds, while the queue returns to empty after 6 minutes) for **cost and stability** (10× fewer workers in this idealised fixed-rate model; consumer admission and downstream capacity still need protection). That trade is acceptable when the product permits the resulting delay, including an explicit pending-job experience.

> [!warning] A queue is not infinite capacity
> Load levelling only works if the **average** arrival rate is below the processing rate. If arrivals average 250 per second and you can do 200, the backlog grows forever. A queue hides overload; it does not fix it. Always alarm on queue depth and on the age of the oldest message.

## Little's Law: a useful sanity check

Little's Law says that, in a stable system, the average number of items in it equals arrival rate × average time spent in it: **L = λ × W**.

If a queue receives 400 messages per second and holds a steady 12,000 messages, each message waits on average 12,000 ÷ 400 = 30 seconds. This turns "queue depth" (which dashboards show) into "delay" (which users feel).

## When to choose which

| Situation | Better fit |
|---|---|
| User needs the answer now | Sync |
| Work can finish later | Async |
| Downstream is slow or flaky | Async |
| Strong read-after-write needed | Sync |
| Many systems react to one fact | Async (pub/sub) |

A common shape is **sync at the edge, async inside**. The checkout API synchronously authorises the payment (the user needs to know), writes the order, then reliably publishes `OrderPlaced`, for example via an outbox committed with the order. Email, analytics, loyalty points and warehouse picking all happen asynchronously.

## The costs of going async

Asynchrony is not free. It moves complexity rather than removing it:

- **Eventual consistency.** The user may see "order placed" before the loyalty points appear. The UI and product need to tolerate that.
- **No direct error path.** If the email worker fails, it cannot return a 500 to the user. You need retries, dead-letter queues and alerts instead.
- **Duplicate and out-of-order delivery.** Most brokers deliver at least once, so consumers must be idempotent. Later lessons cover this in depth.
- **Harder debugging.** A request's story is split across processes and time. You need correlation IDs and distributed tracing (for example, propagating a W3C `traceparent` header in message attributes).
- **One more system to run.** The broker itself must be highly available, monitored and capacity-planned.

> [!tip] Async request-reply
> Sometimes you need a result but the work is slow (video transcoding, report generation). Return `202 Accepted` with a job ID, process via a queue, and let the client poll a status endpoint or receive a webhook. Webhooks and WebSockets are covered in the API design module.

## Brokers you will meet

- **Amazon SQS, RabbitMQ, Azure Service Bus**: message queues. A message is handed to one consumer and deleted once acknowledged.
- **Amazon SNS, Google Pub/Sub**: publish/subscribe. One message is copied to many subscribers.
- **Apache Kafka, Amazon Kinesis, Redpanda**: distributed logs. Messages are appended and retained; consumers track their own position and can replay.

The next lessons take each family in turn.

## Key takeaways
- Required synchronous dependencies multiply availability under independent failures, add critical-path latency and couple load.
- Durable broker configuration, acknowledgements and retention let producers and consumers be decoupled in time and rate while hiding consumer addresses.
- Queue-based load levelling lets you provision for average load rather than peak, at the cost of delay.
- A queue cannot fix sustained overload: watch depth and oldest-message age, and use Little's Law to convert depth into delay.
- Async brings eventual consistency, duplicate delivery and harder debugging, so use it where the caller does not need an immediate answer.

## Further reading
- [Queue-Based Load Leveling pattern (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/queue-based-load-leveling)
- [What is a message queue? (AWS)](https://aws.amazon.com/message-queue/)
- [Avoiding insurmountable queue backlogs (Amazon Builders' Library)](https://aws.amazon.com/builders-library/avoiding-insurmountable-queue-backlogs/)
- [Little's law (Wikipedia)](https://en.wikipedia.org/wiki/Little%27s_law)
- [Enterprise Integration Patterns: Messaging](https://www.enterpriseintegrationpatterns.com/patterns/messaging/)
