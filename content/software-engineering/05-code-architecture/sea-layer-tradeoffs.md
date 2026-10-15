---
id: sea-layer-tradeoffs
sourceLesson: sea-layered
title: Layering trade-offs and framework coupling
level: basic
minutes: 4
summary: Compare strict and relaxed layering and recognise sinkholes, anaemic models and storage coupling.
---

A layered design separates responsibilities, but the boundaries must earn their cost. This unit compares common variants and their failure modes.

## Strict vs relaxed layering

In **strict** (closed) layering, each layer may only call the one directly below. In **relaxed** (open) layering, a layer may skip down several levels, for example a view reading from the data layer directly for a simple report.

| Style | Benefit | Cost |
|---|---|---|
| Strict | Access goes through adjacent layers | Boilerplate pass-through code |
| Relaxed | Less ceremony | More places depend on low layers |

Strict layering can produce **architecture sinkhole** paths: requests that fall straight through every layer with no logic added. A `get_user` view calls `UserService.get_user`, which calls `UserRepository.get_user`, which runs one query. A few sinkhole paths are fine. If most requests look like this, the layers are adding ceremony rather than value, and a relaxed rule (or a simpler design) is better.

## Where layering is used

- **Django** apps blur presentation and data: models are ORM classes and usually hold domain logic too ("fat models"). Many teams add a `services.py` module per app as an application layer.
- **Rails** follows a similar Active Record style.
- **Java enterprise** stacks (Spring) commonly use controller, service and repository layers, almost exactly the diagram above.
- **Network reference models** (the OSI model and the TCP/IP model) and operating systems are layered in the same spirit: they illustrate layered responsibilities, although real implementations include cross-layer interactions and do not all follow this exact import rule.

## How layering goes wrong

### The database becomes the centre

In the classic diagram the data layer is at the bottom, and a literal downward dependency implementation couples the domain to storage. This is not inevitable in every layered design. In practice this means domain classes import the ORM, inherit from `models.Model` and are shaped like tables. Changing storage or testing the rules without a database becomes hard.

This is the weakness that the later ports-and-adapters and clean-architecture units fix by inverting the dependency: the domain defines the interface it needs, and the data layer implements it.

### The anaemic domain

When layers are introduced mechanically, the domain classes often end up as bags of fields with getters and setters, and all logic moves into services. Fowler calls this the **anaemic domain model**. You pay for the layers but get procedural code with extra steps.

## Key takeaways
- Strict layering permits only adjacent calls; relaxed layering allows downward skips.
- Many pass-through layers can add ceremony without hiding useful decisions.
- Domain logic tied to ORM machinery can be harder to reuse outside its framework.
- An anaemic domain model moves rich-model business decisions into services; conditional orchestration alone is not a fault.

## Further reading
- [Presentation Domain Data Layering — Martin Fowler](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)
- [Anemic Domain Model — Martin Fowler](https://martinfowler.com/bliki/AnemicDomainModel.html)
- [Software Architecture Patterns — Mark Richards](https://www.oreilly.com/content/software-architecture-patterns/)
