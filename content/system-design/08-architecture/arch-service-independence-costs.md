---
id: arch-service-independence-costs
title: The cost of service independence
level: basic
minutes: 3
summary: Model required-service availability and see why separate data owners change transaction design.
sourceLesson: arch-monolith-vs-microservices
---

The previous unit distinguished deployment shapes. This unit asks what changes when a call crosses the network and each service owns its database.

## What microservices buy, and what they cost

Microservices let **teams** move independently:

- Each team deploys on its own schedule, without coordinating a release train.
- Services scale independently: the search service gets 40 instances, the admin service gets 2.
- Technology can differ where it matters (a Go service for a latency-critical path, Python for ML).
- A failure can be contained: if recommendations are down, checkout can still work, *if* you designed for it.

The cost is that you've turned a single program into a **distributed system**:

| Concern | Monolith | Microservices |
|---|---|---|
| Call cost | No network transport; can fail | Adds transport and partial failures |
| Transactions | Local ACID can span modules | Local ACID; coordination across owners |
| Debugging | Stack trace | Distributed tracing |
| Deploys | 1 pipeline | N pipelines |
| Data joins | SQL JOIN | API calls or copies |

Every network hop adds latency and a new failure mode. When a request needs *every* service in a chain to work, the chances multiply: the request succeeds only if service 1 works **and** service 2 works **and** so on. Assuming the services fail independently of each other, the combined availability is:

```formula reference
A_total = A_1 × A_2 × ... × A_n
A_total = A^n
where
A_total: the fraction of requests (or time) for which the whole chain works, between 0 and 1 (0.994 = 99.4 %)
A_1: the availability of the first required service, a fraction between 0 and 1
A_2: the availability of the second required service, likewise
...: and so on, one factor per required service
A_n: the availability of the last (nth) required service
A: the availability of each service when they are all the same, e.g. 0.999 (99.9 %); the second line is the shortcut for that case
n: the number of services the request must pass through, all of which must succeed
^: "to the power of": A^n means n copies of A multiplied together
%: per cent; 99.9 % = 0.999
In words: the chain is only as available as all its links together, so an extra fallible required service can lower overall availability.
```

This is a simplified model: it assumes failures are independent (in reality, a shared database or network outage can take several services down together) and that every service is strictly required. Carefully designed fallbacks can reduce required dependencies; retries can also amplify overload, and timeouts only bound waiting rather than guarantee success. You now need service discovery, distributed tracing, centralised logging, contract testing and a platform team to run it all.

### Coordinating a business transaction

An order and a stock reservation can share one local ACID transaction before extraction. With separate Orders and Inventory databases, and no distributed atomic-commit protocol, a **saga** coordinates several local transactions instead.

Orders first creates a pending order and an outbox record in one local transaction. A relay publishes the event; Inventory reserves stock and publishes its outcome reliably. Orders confirms the order, or cancels it through a compensating action if reservation fails. The business must accept the intermediate pending state. Handlers need idempotency, retries and reconciliation, including failed compensation; compensation is an explicit business action rather than automatic isolation or rollback.

A **transactional outbox** makes the business change and the pending event durable together. The relay can publish a duplicate after a crash, so consumers still need deduplication.

> [!analogy] Real-world analogy: A journey with connections
> A journey requiring several connecting trains fails if any required connection is missed.
>
> **How it maps:** Each required service is a necessary connection; adding one adds another condition for the overall request to succeed.
>
> **Where it stops:** Train failures may share a cause, just as services can share infrastructure. The comparison does not justify treating failures as independent.

## Key takeaways
- Independent deployment and scaling require deliberate failure isolation; separation alone does not provide it.
- More required dependencies add failure conditions; a simple availability product requires independent failures.
- A saga coordinates local transactions and compensation; reliable publication and reconciliation remain necessary.

## Further reading
- [Martin Fowler: Microservices](https://martinfowler.com/articles/microservices.html)
- [microservices.io: Saga pattern](https://microservices.io/patterns/data/saga.html)
- [microservices.io: Transactional outbox](https://microservices.io/patterns/data/transactional-outbox.html)
