---
id: pattern-costs-and-scales
title: Pattern costs and wider catalogues
level: basic
minutes: 3
sourceLesson: pattern-why
summary: Introduce indirection to handle real variation rather than a speculative future.
---

## When patterns hurt

Patterns are a means, not a goal. Common ways they go wrong:

- **Pattern-first design.** Starting with "let's use the abstract factory" and then looking for a problem. Start from the change you expect, then pick the shape that makes it cheap.
- **Speculative flexibility.** Adding a strategy interface for a rule that has only ever had one implementation. That is a YAGNI violation: you pay the indirection now for flexibility you may never need.
- **Java in Python.** Writing `AbstractShapeFactoryInterface` classes in a language where a dictionary of functions would do.
- **Cargo-culting the diagram.** Copying the GoF structure exactly when only part of it applies.

> [!warning] Indirection has a price
> Each pattern adds a layer between "what happens" and "where it is written". That layer is worth it when it absorbs real change. When it does not, it is just harder code to read and debug.

A good rule: **refactor towards a pattern** when the second or third variation shows up, rather than designing for it on day one. Joshua Kerievsky's book *Refactoring to Patterns* (2004) is built on this idea.

## Patterns beyond the GoF

The GoF catalogue is about designing *classes and objects*. Other catalogues work at different scales:

- **Enterprise application patterns** (Martin Fowler, 2002): repository, unit of work, data mapper, active record.
- **Integration patterns** (Hohpe and Woolf, 2003): message channel, publish-subscribe, dead letter channel.
- **Concurrency patterns:** producer-consumer, thread pool, reactor.
- **Architectural patterns:** layered, hexagonal, microservices, event sourcing.

The idea is the same at every scale: a named problem, a reusable solution and an honest list of consequences.

## Key takeaways
- Introduce indirection to handle real variation rather than a speculative future.
- Refactor towards a pattern when the changing part becomes clear.
- Enterprise, integration and architectural catalogues apply the same idea at different scales.

## Further reading
- [Design Patterns — publisher catalogue](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-software-9780201633610)
- [Patterns of Enterprise Application Architecture — Martin Fowler](https://martinfowler.com/eaaCatalog/)
- [Design Patterns (the GoF book) — Wikipedia](https://en.wikipedia.org/wiki/Design_Patterns)
- [Software design pattern — Wikipedia](https://en.wikipedia.org/wiki/Software_design_pattern)
- [A Pattern Language — Wikipedia](https://en.wikipedia.org/wiki/A_Pattern_Language)
- [Design Patterns in Dynamic Languages — Peter Norvig](https://norvig.com/design-patterns/)
- [Composition over inheritance — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/composition-over-inheritance/)
- [Design patterns catalogue — Refactoring.Guru](https://refactoring.guru/design-patterns/catalog)
