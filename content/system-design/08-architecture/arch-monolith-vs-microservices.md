---
id: arch-monolith-vs-microservices
title: Monoliths, modular monoliths and microservices
level: basic
minutes: 12
summary: How to decide where the boundaries between deployable units go, why Conway's law matters, and how to avoid building a distributed monolith.
---

Every system has to answer one structural question early: **how many separately deployable pieces should it have?** The answer shapes how teams work, how failures spread, how fast you can ship and how much your infrastructure costs.

There are three broad shapes. None of them is "best". Each is a different set of trade-offs.

## The three shapes

```
 Monolith        Modular monolith
+----------+     +----------------+
| UI       |     | [Orders ]      |
| Orders   |     | [Billing]      |
| Billing  |     | [Catalog]      |
| Catalog  |     |  one process   |
+----+-----+     +-------+--------+
     |                   |
   [ DB ]              [ DB ]
                    (schema per module)

 Microservices
[Orders]   [Billing]   [Catalog]
   |           |           |
 [DB1]       [DB2]       [DB3]
```

- **Monolith**: an application deployed as one unit (often replicated behind a load balancer). Modules commonly call each other in-process and may share a database; a particular repository layout or exactly one database is not required.
- **Modular monolith**: still one deployable, but the code is split into modules with **enforced boundaries**: each module owns its tables, exposes a public interface, and other modules may not reach into its internals. Shopify's core is the famous example, a very large Rails monolith split into components with tooling that flags boundary violations.
- **Microservices**: each business capability is its own service with its own process, its own deployment pipeline and, crucially, **its own data**. Services talk over the network (HTTP/gRPC or messages).

## What a monolith gives you for free

It's easy to undersell the monolith. Inside one process you get:

- **Function calls instead of network calls.** An ordinary call avoids network transport latency and uncertainty about remote delivery. The function can still block, throw after partial state changes, or be interrupted by a process crash; local calls are not automatically atomic.
- **ACID transactions across features.** Placing an order and decrementing stock can be one database transaction.
- **Simple refactoring.** Renaming an interface is an IDE operation, not a multi-team API migration.
- **One thing to deploy, monitor and debug.** A stack trace can show an in-process call chain; asynchronous work and external dependencies still need tracing or correlated logs.

The costs show up with scale, of the *organisation* more than of traffic:

- Build and test times grow; a 40-minute CI pipeline slows everyone.
- A bad release can affect the whole application; staged deployment and isolation can limit the impact.
- Everything scales together. If image resizing needs 30 CPU-heavy boxes, you run 30 copies of the whole app.
- Without discipline, the code becomes a "big ball of mud" where everything depends on everything.

> [!note] A monolith still scales horizontally
> "Monolith" describes the deployment unit, not the instance count. Running 50 stateless copies of one app behind a load balancer is normal and handles very high traffic. Stack Overflow famously served huge traffic from a small number of monolithic servers.

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

> [!note] Evidence gap
> Generic nanosecond-versus-millisecond call timings are omitted because no reproducible benchmark or execution environment was supplied. Measure the actual local and remote operations.

Every network hop adds latency and a new failure mode. A request that fans out through 6 services, each independently 99.9% available and all required, has an availability of roughly 0.999^6 ≈ 99.4% under that simplified model. Carefully designed fallbacks can reduce required dependencies; retries can also amplify overload, and timeouts only bound waiting rather than guarantee success. You now need service discovery, distributed tracing, centralised logging, contract testing and a platform team to run it all.

## Conway's law

> "Any organisation that designs a system will produce a design whose structure is a copy of the organisation's communication structure." Melvin Conway, 1968

Eric Raymond's well-known paraphrase: if four groups work on a compiler, you get a four-pass compiler. If your payments and checkout teams barely talk, the interface between their services will be awkward and slow to change.

This works in both directions:

- **Descriptive**: communication patterns constrain and influence architecture; this is an organizational observation, not a deterministic prediction from team count.
- **Prescriptive** (the "inverse Conway manoeuvre"): design the team structure you want the architecture to have. If you want an independent search service, create a team that owns search end to end.

The deepest reason to adopt microservices is organisational: they let you give a team **full ownership** of a capability, including its data and on-call. With 8 engineers, that benefit is small. With 400, it can be decisive.

## When to split

Martin Fowler's "Monolith First" advice is widely followed: start with a well-structured monolith, learn where the real boundaries are, then extract services when you have a concrete reason. Good reasons include:

1. **Team contention.** Many teams are blocked on each other's deploys or merge conflicts in one codebase.
2. **Different scaling profiles.** One component (video transcoding, search indexing) needs very different hardware or scale.
3. **Different reliability or security needs.** Card handling might need PCI isolation; a flaky experimental feature shouldn't share a process with checkout.
4. **Different change rates.** A pricing engine that changes daily next to a ledger that changes yearly.

Bad reasons: "Netflix does it", "it's modern", or a CV-driven rewrite.

### Finding the boundaries

Business capabilities (orders, billing, inventory) can guide boundaries. A DDD bounded context is the scope in which a domain model and its language are consistent; it is not simply a synonym for a capability or necessarily one service. Avoid mechanically splitting every technical layer into a service. A "database service" or "validation service" that every request passes through couples everything to it.

A good boundary has **high cohesion inside, low coupling outside**: most changes touch one service, and services exchange a small number of well-defined messages.

Three practical tests for a proposed service:

- **Can it be deployed alone?** If releasing it usually means releasing a neighbour too, the boundary is wrong.
- **Does it own its data?** No other service writes its tables, and nobody else reads them directly.
- **Does a typical feature stay inside it?** Look at the last 20 features and count how many services each would have touched.

Size matters less than these. "Micro" is about independence, not line count. A service per table often fragments a capability and increases coordination. Evaluate the actual change and data-access boundaries rather than using table count as a rule.

When one service needs another's data, it either calls the owner's API at request time (simple, but couples availability and adds latency) or keeps a **local copy** fed by the owner's events (fast and independent, but eventually consistent). Joins that used to be one SQL query become one of those two choices.

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
- Monolith, modular monolith and microservices are trade-offs between simplicity and independent ownership, not stages of maturity.
- Microservices turn function calls into network calls: you pay in latency, partial failure, eventual consistency and operational tooling.
- Conway's law means architecture mirrors team communication; design teams and service boundaries together.
- Start with a well-modularised monolith and split along business capabilities when you have a concrete reason, using the strangler fig pattern.
- A distributed monolith (shared DB, lockstep deploys, chatty sync chains) has the costs of both styles and the benefits of neither.

## Further reading
- [Martin Fowler: Microservices](https://martinfowler.com/articles/microservices.html)
- [Martin Fowler: Monolith First](https://martinfowler.com/bliki/MonolithFirst.html)
- [Martin Fowler: Conway's Law](https://martinfowler.com/bliki/ConwaysLaw.html)
- [Martin Fowler: Strangler Fig Application](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [microservices.io: Monolithic architecture pattern](https://microservices.io/patterns/monolithic.html)
- [Segment: Goodbye Microservices](https://www.twilio.com/en-us/blog/developers/best-practices/goodbye-microservices)
