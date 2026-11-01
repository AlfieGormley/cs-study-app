---
id: sea-layer-tradeoffs
sourceLesson: sea-layered
title: Layering trade-offs and framework coupling
level: basic
minutes: 5
summary: Compare strict and relaxed layering and recognise sinkholes, anaemic models and storage coupling.
---

A layered design separates responsibilities, but the boundaries must earn their cost. This unit compares common variants and their failure modes.

## Strict vs relaxed layering

In **strict** (closed) layering, each layer may only call the one directly below. In **relaxed** (open) layering, a layer may skip down several levels, for example a view reading from the data layer directly for a simple report.

| Style | Benefit | Cost |
|---|---|---|
| Strict | Access goes through adjacent layers | Boilerplate pass-through code |
| Relaxed | Less ceremony | More places depend on low layers |

Strict layering can produce **architecture sinkhole** paths, a name Mark Richards uses for requests that fall straight through every layer with no logic added. A `get_user` view calls `UserService.get_user`, which calls `UserRepository.get_user`, which runs one query. Every layered system has some. Richards offers a rough rule of thumb: around a fifth of requests passing straight through is typical, but if most requests look like this, the layers are adding ceremony rather than value. Richards suggests considering opening some layers, while noting that this makes change harder to control because the layers are less isolated.

> [!analogy] Real-world analogy: a call put through three receptionists
> You ring a company. The switchboard says "putting you through", a department secretary says "putting you through", and finally you reach the person you wanted. Neither of the first two asked anything or checked anything.
>
> **How it maps:** Each receptionist is a layer, and your call is a request. When nobody on the way adds a check, a decision or a translation, the extra hops are a sinkhole: cost without value. A receptionist who screens calls or takes messages is like a service that enforces permissions or runs a transaction, and earns its place.
>
> **Where it stops:** Receptionists cost wages on every call. A pass-through function costs almost nothing at runtime; its cost is extra code to read, change and test. And a thin layer can still be worth keeping as the agreed place where logic will go when it appears.

## Where layering is used

- **Django** apps blur domain and data: models are ORM classes and usually hold domain logic too ("fat models"). Many teams add a `services.py` module per app as an application layer.
- **Rails** follows a similar Active Record style.
- **Java enterprise** stacks (Spring) commonly use controller, service and repository layers, almost exactly the diagram above.
- **Network reference models** (the OSI model and the TCP/IP model) and operating systems are layered in the same spirit: they illustrate layered responsibilities, although real implementations include cross-layer interactions and do not all follow this exact import rule.

## How layering goes wrong

### The database becomes the centre

In the classic diagram the data layer sits at the bottom, so if you follow "depend downwards" literally, the domain depends on storage. In practice that means domain classes import the ORM, inherit from `models.Model` and are shaped like tables, and changing storage or testing the rules without a database gets hard. A layered design doesn't have to work this way: mappers or repository interfaces can keep the domain free of storage code.

This is the weakness that the later ports-and-adapters and clean-architecture units fix by inverting the dependency: the domain defines the interface it needs, and the data layer implements it.

### The anaemic domain

When layers are introduced mechanically, the domain classes often end up as bags of fields with getters and setters, and all logic moves into services. Fowler's 2003 article calls this the **anaemic domain model** and treats it as an anti-pattern: you pay for a separate domain layer and an object-relational mapping, but get procedural code with extra steps.

This is a judgement, not a law. Fowler himself notes that a domain model isn't always the best tool; his alternative for simpler logic is the **transaction script**, one procedure per request, and many teams, including those writing in a functional style, deliberately keep data and behaviour apart. The criticism bites when you have chosen a rich domain model and then let its behaviour drain into services.

## Key takeaways
- Strict layering permits only adjacent calls; relaxed layering allows downward skips.
- Many pass-through layers can add ceremony without hiding useful decisions.
- Domain logic tied to ORM machinery can be harder to reuse outside its framework.
- An anaemic domain model moves business decisions out of domain objects into services; Fowler calls it an anti-pattern, but transaction scripts suit simple logic.

## Further reading
- [Presentation Domain Data Layering — Martin Fowler](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)
- [Anemic Domain Model — Martin Fowler](https://martinfowler.com/bliki/AnemicDomainModel.html)
- [Software Architecture Patterns — Mark Richards](https://www.oreilly.com/content/software-architecture-patterns/)
- [Transaction Script — Martin Fowler](https://martinfowler.com/eaaCatalog/transactionScript.html)
