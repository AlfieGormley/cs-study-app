---
id: sea-module-dependency-stability
sourceLesson: sea-modularity
title: Acyclic dependencies and instability
level: advanced
minutes: 5
summary: Identify package cycles and judge which way dependencies should point using Martin's stability idea.
---

After choosing module boundaries, inspect the arrows between them. This unit introduces package principles and measures stability by dependency direction.

## Dependency direction: the package principles

Robert C. Martin's package principles turn "point dependencies the right way" into rules you can check.

### ADP: no cycles

The **Acyclic Dependencies Principle**: the dependency graph between packages must have no cycles.

```
 cyclic                 acyclic
 orders --> billing     orders --> billing
   ^          |            |          |
   |          v            v          v
   +----- customers       customers <-+
```

With a cycle, the three packages behave as one: isolated testing, reasoning and extraction become harder, and a change to any can ripple to all.

### SDP: depend towards stability

The **Stable Dependencies Principle**: depend in the direction of stability. A package that many others depend on is hard to change (it is *stable* in Martin's sense, meaning costly to change, not "rarely buggy").

> [!analogy] Real-world analogy: foundations and light fittings
> In a house, the walls, floors and roof all rest on the foundations, so changing the foundations is a major job. A light fitting depends on the ceiling, but nothing depends on it, so you can swap it in an afternoon. You attach light fittings to the structure, never the other way round.
>
> **How it maps:** A package many others depend on is like the foundations: stable in Martin's sense, because changing it disturbs everything resting on it. A package nobody depends on is like a light fitting: unstable, cheap to change. SDP says the dependency arrows should go from the fittings to the foundations.
>
> **Where it stops:** Foundations are also hard to change physically. A stable package is often trivially easy to edit; the cost is in everyone who depends on it. And software has a way to make a stable package flexible, abstract interfaces, which the next unit explores.

Martin turned this into a number by counting dependency arrows. Arrows coming in mean other code will break if this package changes; arrows going out mean this package can be broken by changes elsewhere. His **instability** is the share of a package's arrows that point outwards.

```formula reference
I = Ce / (Ca + Ce)
where
I: the instability of one package, a number from 0 (maximally stable) to 1 (maximally unstable); it is a ratio of two counts, so it has no unit
Ce: efferent couplings: how many other packages this package depends on (imports), its outgoing arrows
Ca: afferent couplings: how many other packages depend on (import) this package, its incoming arrows
In words: instability is the fraction of a package's dependency arrows that point outwards. A package that imports others and is imported by nobody scores 1; one that is imported by others and imports nothing scores 0.
```

For example, a `billing` package imported by `orders` and `checkout`, and importing only `money`, has one outgoing arrow out of three: an instability of about a third, so fairly stable. A web package that imports four others and is imported by nothing has instability 1; a `money` package imported by four others that imports nothing has instability 0.

Two caveats. Martin's 1994 definition counts *classes* on each side of the boundary; counting whole packages, as here, is a common simplification that can give different numbers. And a package with no dependencies in either direction gives 0 divided by 0, which tools handle by their own convention.

Volatile code (UI, integrations, experiments) should be unstable in this sense, with nothing much depending on it, and should depend on stable code, never the other way round. If a stable core package imports a volatile one, every experiment risks breaking the core.

The related **Stable Abstractions Principle** says stable packages should be abstract (interfaces or abstract types; a pure calculation is not automatically abstract) so they can be extended without being modified. That is why ports, owned by the core, sit at the stable end.

## Key takeaways
- Dependency cycles increase coupling and hinder independent reasoning.
- Stable means costly to change because other code depends on it.
- Volatile packages should depend on stable ones, never the reverse.
- Martin's instability is the share of a package's dependency arrows that point outwards; package counts simplify his class counts.

## Further reading
- [OO Design Quality Metrics — Robert C. Martin](https://condor.depaul.edu/dmumaugh/OOT/Design-Principles/oodmetrc.pdf)
