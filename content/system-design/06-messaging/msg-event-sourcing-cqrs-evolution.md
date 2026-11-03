---
id: msg-event-sourcing-cqrs-evolution
title: Event sourcing, CQRS and historical evolution
level: advanced
minutes: 3
summary: Rebuild state from events while managing snapshots, concurrent writes, schema changes and lagging read models.
sourceLesson: msg-event-driven-architecture
---

Events can also be a service’s durable source of truth. That storage choice is separate from sending notifications to other services, and it creates long-lived obligations for replay and schema evolution.

## Event sourcing

The **events are the source of truth**. Instead of storing an account's current balance, you store every `Deposited` and `Withdrew` event, and derive the balance by replaying them.

```
stream: account-42
 1 Opened       {}
 2 Deposited    {100}
 3 Withdrew     {30}
 4 Deposited    {50}
```

Starting from an empty account, applying those deposits and withdrawal leaves £120. The event history is authoritative; the current balance may also be stored as a derived projection or snapshot. Rebuilding means applying the same events in order, not treating the derived balance as an independent source of truth.

> [!analogy] Real-world analogy: a bank statement and its closing balance
> A statement lists deposits and withdrawals. Its closing balance can be checked by following those entries from the opening balance.
>
> **How it maps:** Recorded entries correspond to events; the calculated balance corresponds to derived state. A saved balance at an agreed entry is like a snapshot from which later entries can be applied.
>
> **Where it stops:** A statement can omit the wider system's activity. Event sourcing requires a deliberate complete event history for the aggregate, concurrency control and compatible replay logic; the comparison does not establish audit or legal compliance.

Benefits:

- A history of recorded domain changes; audit completeness, actor identity, integrity and access controls still require design.
- **Temporal queries**: what was the balance on 1 March?
- New read models can be built later by replaying history.

Costs:

- Replaying long streams is slow, so you take periodic **snapshots** (state at event 10,000) and replay from there.
- Events are immutable, so changing their schema needs **upcasting** (transforming old versions when read) or versioned handlers.
- Personal-data erasure needs a design covering logs and derived copies. Crypto-shredding can make previously encrypted fields inaccessible only when all usable key copies are destroyed; plaintext copies and metadata remain separate concerns. A claim of GDPR compliance for a specific deployment is absent because the necessary legal and technical conditions were not established in this audit.
- Writes usually need **optimistic concurrency** on the stream: append event 5 only if the stream is still at version 4.

Event sourcing is a **storage** pattern inside one service. It does not require a message broker, and the internal events need not be the events you publish to other services.



## CQRS

**Command Query Responsibility Segregation** splits the model used to change data (commands) from the model(s) used to read it (queries).

```
 command ─▶ write model ─▶ events
                              │
              ┌───────────────┤
              ▼               ▼
         read model A    read model B
         (Postgres)      (Elasticsearch)
              ▲               ▲
            query           search
```

Each read model is denormalised for one access pattern. CQRS pairs naturally with event sourcing (event projections are built from the event stream) but does not require it.

With asynchronously maintained read stores, the price is **eventual consistency between write and read**: after a command succeeds, a projection may lag. CQRS itself does not require separate databases or asynchronous propagation; separate models can share one transactionally updated store. UIs must handle it, for example by returning the new state from the command, or by waiting for the projection to reach a version.

> [!warning] Use sparingly
> Fowler's advice is that CQRS suits specific bounded contexts with complex domains or very different read and write loads. Applied to a whole system by default, it adds a great deal of complexity for little gain.

## Key takeaways

- Event sourcing makes recorded events authoritative; snapshots shorten rebuilding and upcasters adapt old payloads.
- Expected stream versions prevent two writers accepting incompatible simultaneous changes.
- CQRS separates read and write models; asynchronous projections need a version-aware or optimistic UI.
- Erasure must cover usable keys and derived plaintext copies; encrypted append-only storage alone does not establish legal compliance.

## Further reading

- [Event Sourcing (Martin Fowler)](https://martinfowler.com/eaaDev/EventSourcing.html)
- [CQRS (Martin Fowler)](https://martinfowler.com/bliki/CQRS.html)
- [Python round semantics](https://docs.python.org/3/library/functions.html#round)
