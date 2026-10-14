---
id: dist-saga-control-outbox
title: Saga control, isolation and the outbox
level: advanced
minutes: 3
summary: Choose a durable workflow style and publish events reliably without pretending intermediate state is isolated.
sourceLesson: dist-transactions
---

The preceding unit explained saga compensation and the danger of late requests. A real saga also needs durable control, a plan for intermediate state and reliable event publication.

### Orchestration versus choreography

| | Orchestration | Choreography |
|---|---|---|
| Control | Central orchestrator | Services react to events |
| Visibility | Saga state in one place | Spread across services |
| Coupling | Orchestrator knows all | Services know events |
| Best for | Complex, many steps | Short, simple flows |

**Orchestration**: an orchestrator (a state machine, often built on Temporal, AWS Step Functions or Camunda) tells each service what to do and handles failures. The orchestrator's own state must be durable, so a crash mid-saga resumes where it left off; durable-execution engines like Temporal exist largely to provide that.

```
Orchestrator
 |--reserve stock--> Inventory
 |<--ok-------------
 |--charge---------> Payments
 |<--declined-------
 |--release stock--> Inventory
```

**Choreography**: each service publishes events and others subscribe. `OrderCreated` triggers Payments; `PaymentFailed` triggers Inventory to release stock and Orders to cancel. There's no central coordinator, but the flow is implicit and harder to trace or change, and cyclic dependencies creep in.

### Isolation: the saga's weakness

Sagas preserve local transaction guarantees but do not provide global ACID atomicity or isolation; compensation is a later business action, not an invisible rollback. Other transactions see intermediate states: a product shows "reserved" stock for an order that's about to be cancelled, or a balance briefly includes a charge that will be refunded. Anomalies include **lost updates** and **dirty reads** across steps. Countermeasures:

- **Semantic locks**: mark records as PENDING so others treat them carefully.
- **Commutative updates**: design steps so order doesn't matter (increment/decrement).
- **Re-reading values** before acting, or versioning records.

### Reliable messaging

Every step needs "update my database *and* publish an event" atomically, otherwise a crash between them stalls the saga. The standard fix is the **transactional outbox**: write the event to an `outbox` table in the same local transaction, and have a relay (or CDC tool like Debezium) publish it. Consumers must deduplicate, because delivery is at least once.

## Choosing

| Situation | Use |
|---|---|
| Shards of one database | 2PC over consensus groups |
| Few systems, short, need atomicity | 2PC/XA (carefully) |
| Microservices, long-running flow | Saga |
| Can redesign boundaries | Avoid it: one service owns the data |

## Key takeaways
- Orchestration centralises durable saga state; choreography spreads control across event reactions.
- Sagas expose intermediate state, so semantic locks, commutative updates and version checks help manage anomalies.
- The transactional outbox commits data and event intent together; its relay may repeat delivery, so consumers deduplicate.

## Further reading
- [Sagas (Garcia-Molina and Salem, 1987)](https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf)
- [Saga pattern (microservices.io)](https://microservices.io/patterns/data/saga.html)
- [Saga distributed transactions (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga)
- [Compensating Transaction pattern (Azure)](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)
