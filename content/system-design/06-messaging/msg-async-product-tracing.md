---
id: msg-async-product-tracing
title: Choose async work and keep the user informed
level: basic
minutes: 2
summary: Place work according to the response users need, then handle pending results, failures and tracing.
sourceLesson: msg-sync-vs-async
---

An asynchronous design changes the promise the product makes. Accepting a job means it will be attempted later; it does not mean its database write or external side effect has already succeeded.

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

## Key takeaways

- Keep work required for the immediate success response on that response path.
- Slow jobs can return a job ID with 202 Accepted, then expose status or notify the client.
- Asynchronous writes require an explicit pending-state experience; message trace context connects the request to later work.

## Further reading

- [Queue-Based Load Leveling pattern (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/queue-based-load-leveling)
- [Avoiding insurmountable queue backlogs (Amazon Builders' Library)](https://aws.amazon.com/builders-library/avoiding-insurmountable-queue-backlogs/)
- [Enterprise Integration Patterns: Messaging](https://www.enterpriseintegrationpatterns.com/patterns/messaging/)
