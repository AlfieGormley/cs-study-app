---
id: arch-message-command-event-boundaries
title: Choosing calls, commands and events
level: intermediate
minutes: 4
summary: Decide which results need an immediate reply and publish asynchronous effects reliably.
sourceLesson: arch-service-communication
---

After discovery and traffic policy, choose the business interaction itself. A payment authorisation may be required now; confirmation email usually can wait without holding checkout open.

## Synchronous versus asynchronous calls

This choice matters more than which discovery mechanism you pick.

### Synchronous (request/response)

Orders calls Payments over HTTP or gRPC and **waits** for the answer.

- Simple to reason about; the caller gets an immediate result.
- **Temporal coupling**: Payments must be up *right now* for Orders to succeed.
- Latency adds up along the chain, and slow dependencies retain caller resources. Blocking clients hold threads; asynchronous clients can still retain requests, connections and memory.

### Asynchronous (messaging)

Orders publishes `OrderPlaced` to a broker (Kafka, SQS, RabbitMQ) and returns. Payments consumes it when it can.

- The producer doesn't need the consumer to be up; the broker buffers.
- Natural load levelling and fan-out to many consumers.
- **Eventual consistency**: the user may see "processing" for a while.
- Harder to debug, and you must handle duplicates and ordering.

| Need | Prefer |
|---|---|
| User needs answer now | Sync |
| Read data for a page | Sync (or cache) |
| Side effects (email) | Async |
| Many consumers | Async events |
| Spiky workloads | Async queue |

### Commands versus events

Async messages come in two flavours:

- A **command** says "do this" to a specific service: `ChargeCard`. The sender knows who handles it.
- An **event** says "this happened": `OrderPlaced`. The publisher doesn't know or care who listens, which is the loosest coupling.

> [!example] Checkout in practice
> Checkout calls Payments **synchronously** for authorisation, because the user must know whether the card was accepted. It then publishes `OrderPlaced`. Inventory, Email, Analytics and Loyalty consume that event **asynchronously**. If Email is down for an hour, checkout is unaffected and delivery can resume when it recovers, provided durable retention, retries and deduplication cover the outage and the provider accepts the messages.

## Protocols in brief

- **REST/JSON over HTTP**: universal and easy to debug; verbose, and contracts are often informal (OpenAPI helps).
- **gRPC**: Protocol Buffers over HTTP/2; compact, fast, strongly typed contracts and streaming; less friendly to browsers and curl. Common for internal service-to-service calls.
- **Messaging**: Kafka for high-throughput replayable event logs; SQS or RabbitMQ for work queues.

An **API gateway** usually sits at the edge, handling auth, rate limiting and routing for external clients, while internal traffic goes service-to-service (often via the mesh).

### Closing the publication gap

Writing an order to the database and then publishing to Kafka leaves a crash gap. Reversing those steps can publish an event for a transaction that never commits. A transactional outbox stores the order and a pending event in the same local transaction; a recovering relay publishes pending records. A relay that crashes after publishing can send the same event again, so consumers deduplicate by event identity. Retention, monitoring and recovery remain required. This preserves the asynchronous design without pretending that the database and broker share one atomic transaction.

## Key takeaways
- Use synchronous calls when the caller requires an immediate result; slow dependencies still hold caller resources.
- Commands request a specific action while events announce a fact to potentially many listeners.
- A durable broker decouples consumer uptime subject to retention, retries, ordering and deduplication.
- Commit the business change with an outbox record before a relay publishes the event.

## Further reading
- [gRPC: Introduction](https://grpc.io/docs/what-is-grpc/introduction/)
- [microservices.io: API gateway](https://microservices.io/patterns/apigateway.html)
- [microservices.io: Transactional outbox](https://microservices.io/patterns/data/transactional-outbox.html)
