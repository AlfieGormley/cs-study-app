---
id: arch-deployment-unit-shapes
title: Choosing a deployment unit
level: basic
minutes: 3
summary: Compare monoliths, modular monoliths and microservices without confusing deployment units with instance counts.
sourceLesson: arch-monolith-vs-microservices
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

## Key takeaways
- A monolith is one deployable, which can run as many stateless instances.
- A modular monolith enforces internal interfaces and data ownership while retaining one deployable.
- In-process calls and shared local transactions simplify coordination, but organisation size and uneven workloads can expose costs.

## Further reading
- [Martin Fowler: Microservices](https://martinfowler.com/articles/microservices.html)
- [microservices.io: Monolithic architecture pattern](https://microservices.io/patterns/monolithic.html)
