---
id: dist-saga-compensation
title: Saga steps, compensation and late work
level: advanced
minutes: 3
summary: Order compensatable and irreversible steps, and prevent delayed forward work from undoing cancellation.
sourceLesson: dist-transactions
---

Long service workflows often cannot hold database locks until the whole business operation finishes. Sagas trade global atomicity for local commits and explicit compensation.

## Sagas

Microservices usually can't (or shouldn't) hold locks across services for the duration of a business process. A **saga** (Garcia-Molina and Salem, 1987) breaks a long transaction into a sequence of **local transactions**, each committed immediately in its own service. If a later step fails, previously completed steps are undone by **compensating transactions**.

```
T1 order    T2 payment   T3 stock
created --> charged ----> reserve FAILS
                              |
C2 refund <-------------------+
C1 cancel order
```

### Compensating actions

A compensation is a *semantic* undo, not a rollback. A refund is not the same as never having charged: the customer may see two lines on their statement. Some actions can't be compensated at all (an email sent, a parcel shipped), so order steps carefully:

1. **Compensatable** steps first (create order in PENDING, reserve stock).
2. The **pivot** step: the point of no return (charge the card).
3. **Retriable** steps after the pivot, which must eventually succeed (send confirmation email, notify warehouse).

Compensations must themselves be **idempotent** and retried until they succeed; if a refund call times out, you retry it.

### Timeouts make it harder

A step that times out has an **unknown** outcome, exactly as in the earlier timeout unit. If the orchestrator gives up on "charge card" and starts compensating, the charge might still happen later: the request could be sitting in a queue. So:

- A compensation must be safe to run even if the forward step **never happened** (refunding an unknown charge is a no-op).
- The service should record the compensation, so a forward request that arrives **after** it is rejected rather than applied. Use a shared saga or step identifier for correlation, with distinct idempotency keys for the forward action and compensation; a durable step state machine must reject late forward work after cancellation.
- Where possible, ask the service for the step's status (by idempotency key) before deciding to compensate.

## Key takeaways
- A saga commits local steps and later compensates completed work after failure; semantic undo is visible to users.
- Put compensatable work before the pivot, then steps that can be retried to eventual success.
- A timeout leaves an unknown outcome; cancellation needs durable correlated state and distinct idempotency keys to reject late forward work.

## Further reading
- [Sagas (Garcia-Molina and Salem, 1987)](https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf)
- [Saga pattern (microservices.io)](https://microservices.io/patterns/data/saga.html)
- [Saga distributed transactions (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga)
- [Compensating Transaction pattern (Azure)](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)
