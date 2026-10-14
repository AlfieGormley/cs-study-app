---
id: arch-gradual-service-extraction
title: Extracting an independent service safely
level: basic
minutes: 3
summary: Use gradual routing and data migration while checking for the distributed-monolith failure mode.
sourceLesson: arch-monolith-vs-microservices
---

The previous unit identified capability boundaries. Now follow one capability into a separate deployable without losing data ownership or a workable rollback.

### How to split safely: the strangler fig

Rewriting from scratch is risky. The **strangler fig** pattern extracts gradually:

```
           +-----------+
 client -->|  routing  |
           +--+-----+--+
   /billing/* |     | everything else
              v     v
       [Billing svc] [Monolith]
```

1. Introduce a routing or interface boundary around the capability.
2. Build the replacement and establish data ownership, migration, validation and write coordination before directing production writes to it.
3. Shift traffic gradually with a tested rollback/data-compatibility plan; retire old code only after remaining readers and writers have migrated.
4. Repeat until the monolith is small or gone.

## The distributed monolith anti-pattern

The worst outcome is paying all the costs of microservices while getting none of the benefits. Signs you've built a **distributed monolith**:

- **Lockstep deploys**: you can't release service A without releasing B and C at the same time.
- **Shared database**: several services read and write the same tables, so a schema change needs every team.
- **Chatty synchronous chains**: one user request triggers a long chain of blocking calls; if any service is down, everything is.
- **Shared domain libraries**: a "common models" package that every service must upgrade together.

> [!warning] The shared database trap
> Two services writing the same table share a data contract and can become tightly coupled; sharing does not literally make their processes one service. Each service should own its data and expose it only through its API or events. Other services that need the data keep their own copy, updated by events.

The fix is usually to **merge** tightly coupled services back together, or to redraw boundaries so each service owns a complete capability and its data. Several companies have publicly consolidated over-split microservices. Segment wrote in 2018 about merging over 140 near-identical destination services back into a single service, after which deploys took minutes, test suites ran far faster and engineers spent less time on operational toil.

> [!example] A sensible middle path
> A 30-engineer startup runs a modular monolith with modules for accounts, orders and notifications, each with its own schema. Notifications needs to send 2 million emails in a burst and is extracted first, consuming `OrderPlaced` events from a queue. Everything else stays in the monolith until there's a reason to move it.

## Key takeaways
- Strangler fig extraction moves one capability at a time behind a routing or interface boundary.
- Break direct data dependencies, coordinate migration and validate rollback before shifting production writes.
- Lockstep releases, shared tables and chatty required chains reveal coupling that service count cannot fix.
- Merge tightly coupled services or redraw ownership rather than preserving a distributed monolith.

## Further reading
- [Martin Fowler: Strangler Fig Application](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [Segment: Goodbye Microservices](https://www.twilio.com/en-us/blog/developers/best-practices/goodbye-microservices)
