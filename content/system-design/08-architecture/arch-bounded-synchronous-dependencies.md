---
id: arch-bounded-synchronous-dependencies
title: Bounding synchronous dependency failures
level: intermediate
minutes: 3
summary: Use deadlines, bulkheads, fallbacks and retry budgets to keep remote failures from consuming the caller.
sourceLesson: arch-service-communication
---

Synchronous request/response creates temporal coupling: a required remote service must respond in time. The goal here is to bound that dependency's resource use and failure impact.

## Making synchronous calls safe

When you do call synchronously, protect the caller:

1. **Timeouts on every call.** Without one, a hung dependency hangs you. Set them from measured latency (for example p99.9 plus margin), and allocate nested calls and retries within the remaining end-to-end deadline, leaving time for local work and response handling.
2. **Retries with exponential backoff and jitter**, only for idempotent operations, with a retry budget to bound additional load during an outage.
3. **Circuit breakers**: after repeated failures, fail fast for a while instead of piling on.
4. **Bulkheads**: bound in-flight work and queues per dependency, with separate resources where needed. Separate connection pools alone do not guarantee isolation of a shared thread pool.
5. **Fallbacks**: serve cached or default data (generic recommendations instead of personalised ones).

Watch out for **retry amplification**. An upstream retry can repeat a whole downstream sequence of attempts, multiplying load when the dependency is already struggling.

When callers at several layers retry, each retry can trigger another set of downstream attempts. With three retrying layers allowing three attempts each, one user request can reach the bottom service 27 times.

This is the worst case. If the bottom service recovers, or some failures are not retried (for example a "400 Bad Request"), the real count is lower.

The usual fix is to retry at **one** layer only (often the one nearest the failing dependency), and to cap retries with a budget, for example retries may add at most 10% to normal traffic.

### Latency budgets are joint measurements

Sequential call durations add for one actual request. Adding several services' individual p99 values only gives a rough scale; it does not calculate the whole request's p99, because slow tails can occur on different requests or be correlated. Measure the end-to-end distribution. If Loyalty points are optional at checkout, publish an order event and show a pending points state rather than adding another required synchronous call.

## Key takeaways
- Allocate nested calls and retries inside the remaining end-to-end deadline and propagate cancellation cooperatively.
- Bulkheads must bound both in-flight work and waiting queues; shared resources can otherwise remain exhausted.
- Retries multiply down a chain; concentrate them and bound extra traffic with a retry budget.
- Remove nonessential work from the required request path and measure the end-to-end latency distribution.

## Further reading
- [Istio architecture](https://istio.io/latest/docs/ops/deployment/architecture/)
- [gRPC: Introduction](https://grpc.io/docs/what-is-grpc/introduction/)
- [AWS Builders' Library: Timeouts, retries and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
