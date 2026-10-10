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

- **Availability multiplies.** If Checkout requires three services that are each 99.9% available and their failures are independent, all three must be up at once, so together they are only about 99.7% available (worked out below). Correlated failures change this calculation, and Checkout has its own failure modes. That is about 26 hours of downtime a year instead of 8.8.
- **Latency adds up.** Sequential dependent calls add their durations; parallel fan-out waits for the required critical path, and tail latency (p99) gets worse as you add hops, because the slowest dependency dominates. If a request touches 5 services with independent delays and each is slow 1% of the time, the request hits at least one slow call about 4.9% of the time (worked out below): tail slowness becomes more frequent at the request level; exact quantiles depend on the full latency distributions.
- **Load is coupled.** A spike at the front door hits every downstream service at the same instant. If Fraud can only handle 500 requests a second, Checkout can only handle 500 requests a second.

Both numbers come from one rule of probability: when events are independent, the chance that all of them happen is the product of their separate chances. For availability, a request that needs every dependency succeeds only when all of them are up:

```formula
A_chain = A_1 × A_2 × A_3
A_chain = 0.999 × 0.999 × 0.999
A_chain ≈ 0.997 = 99.7%
where
A_chain: the availability of the chain: the fraction of time all three dependencies are up together, so the request can succeed (ignoring Checkout's own failures)
A_1: the availability of the first dependency (Payments): the fraction of time it is up, here 0.999 (99.9%)
A_2: the availability of the second dependency (Inventory), here 0.999
A_3: the availability of the third dependency (Fraud), here 0.999
≈: approximately equal to (the result is rounded)
%: per cent; 0.997 is the same as 99.7%
In words: when every dependency is required, multiply their availabilities; three 99.9% services together are only about 99.7% available.
```

To turn an availability into downtime, multiply the fraction of time it is *not* up by the 8,760 hours in a 365-day year:

```formula
D = (1 − A) × 8760 h
D_one = (1 − 0.999) × 8760 h ≈ 8.8 h
D_chain = (1 − 0.997) × 8760 h ≈ 26 h
where
D: expected downtime per year, in hours (h)
A: an availability, as a fraction between 0 and 1
D_one: the yearly downtime of one 99.9% service
D_chain: the yearly downtime of the chain of three, which is about 99.7% available
h: hours
≈: approximately equal to
In words: each extra required dependency adds its own downtime, so three 99.9% services cost about three times the downtime of one.
```

For tail latency, it is easier to work out the chance that *every* call is fast and subtract that from 1:

```formula
P_slow = 1 − (1 − p)^k
P_slow = 1 − 0.99^5
P_slow ≈ 1 − 0.951 = 0.049
where
P_slow: the probability that a request hits at least one slow call, as a fraction (0.049 is 4.9%)
p: the probability that any one call is slow, here 0.01 (1%)
k: the number of independent calls the request must wait for, here 5
^: to the power of; 0.99^5 means 5 copies of 0.99 multiplied together
≈: approximately equal to
In words: if each of 5 calls is fast 99% of the time, all 5 are fast only about 95% of the time, so about 1 request in 20 is slow.
```

Both formulas assume independence. Shared causes (one database, one network link, one bad deploy) make failures and slow calls happen together, so real systems can be better or worse than these numbers, and you should measure.

## Asynchronous: send and carry on

In asynchronous communication, the producer hands a **message** to an intermediary (a broker) and can continue after the required broker acknowledgement without waiting for processing. A consumer picks the message up later, maybe milliseconds later, maybe hours.

```
Checkout ─▶ [ queue ] ─▶ Email worker
   │
   └─▶ responds to user at once
```

With durable queues, suitable publish acknowledgement and retention settings, the broker retains the message, so the producer and consumer do not need to be running at the same time. This is the key idea: **the queue decouples the two sides in time**.

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

Without a queue, you need 20 workers (2,000 ÷ 100) sitting mostly idle to survive the peak. With a queue and 2 workers (200 per second capacity), the backlog grows while arrivals exceed capacity:

```formula
B = (λ_burst − μ) × T_burst
B = (2000/s − 200/s) × 30 s
B = 1800/s × 30 s = 54000 msg
where
B: the backlog: messages waiting in the queue when the burst ends
λ_burst: lambda, the arrival rate during the burst, here 2,000 messages per second
μ: mu, the processing capacity of all workers together, here 2 workers × 100 = 200 messages per second
T_burst: how long the burst lasts, here 30 seconds
s: seconds; "/s" means per second
msg: messages
In words: during a burst the queue grows by the excess of arrivals over capacity, for every second the burst lasts.
```

After the burst, arrivals drop to 50 per second, so the workers eat into the backlog with whatever capacity is left over:

```formula
T_drain = B / (μ − λ_after)
T_drain = 54000 msg / (200/s − 50/s)
T_drain = 54000 msg / 150/s = 360 s
where
T_drain: the time after the burst until the queue is empty again, in seconds (s); 360 s is 6 minutes
B: the backlog at the end of the burst, here 54,000 messages
μ: mu, the total processing capacity, here 200 messages per second
λ_after: lambda, the arrival rate after the burst, here 50 messages per second
msg: messages
s: seconds; "/s" means per second
In words: the backlog shrinks only by the spare capacity left after serving new arrivals, so it takes 6 minutes to clear, not 54,000 ÷ 200 = 4.5 minutes.
```

The message at the back of the burst waits roughly as long as it takes the workers to get through everything in front of it:

```formula
W_max ≈ B / μ
W_max ≈ 54000 msg / 200/s = 270 s
where
W_max: the longest wait in first-in, first-out (FIFO) order: the wait of the last message of the burst, in seconds (s)
B: the backlog at the end of the burst, 54,000 messages
μ: mu, the total processing capacity, 200 messages per second
≈: approximately equal to
msg: messages
s: seconds; "/s" means per second
In words: the last message of the burst waits about 4.5 minutes, because 54,000 messages are ahead of it and the workers do 200 a second.
```

So you trade **latency** (the longest wait is about 270 seconds, while the queue returns to empty after 6 minutes) for **cost and stability** (10× fewer workers in this idealised fixed-rate model; consumer admission and downstream capacity still need protection). That trade is acceptable when the product permits the resulting delay, including an explicit pending-job experience.

> [!warning] A queue is not infinite capacity
> Load levelling only works if the **average** arrival rate is below the processing rate. If arrivals average 250 per second and you can do 200, the backlog grows forever. A queue hides overload; it does not fix it. Always alarm on queue depth and on the age of the oldest message.

## Little's Law: a useful sanity check

Little's Law says that, in a stable system (one where, over time, items leave as fast as they arrive), the average number of items in it equals the arrival rate times the average time each item spends in it. Rearranged, it tells you the average wait from two numbers a dashboard already shows:

```formula
L = λ × W
W = L / λ
W = 12000 msg / 400/s = 30 s
where
L: the average number of items in the system; for a queue, the average queue depth, here 12,000 messages
λ: lambda, the average arrival rate, here 400 messages per second
W: the average time an item spends in the system, in seconds (s)
msg: messages
s: seconds; "/s" means per second
In words: average depth equals arrival rate times average wait, so depth divided by arrival rate gives the average wait.
```

So a queue that receives 400 messages per second and holds a steady 12,000 makes each message wait about 30 seconds on average. This turns "queue depth" (which dashboards show) into "delay" (which users feel). It holds for long-run averages in a stable system; while a queue is growing during a burst, the momentary numbers need not match it.

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
- **No direct error path.** If the email worker fails, it cannot return an HTTP 500 error to the user. You need retries, dead-letter queues and alerts instead.
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
