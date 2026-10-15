---
id: sea-module-dependency-stability
sourceLesson: sea-modularity
title: Acyclic dependencies and instability
level: advanced
minutes: 5
summary: Identify package cycles and calculate instability from incoming and outgoing dependencies.
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

To make "stable" measurable, Martin counts the dependency arrows into and out of a package. Arrows coming in mean other code will break if this package changes; arrows going out mean this package can be broken by changes elsewhere. His measure of **instability** is the share of arrows that point outwards:

```formula
I = Ce / (Ca + Ce)
where
I: the instability of one package, a number from 0 (maximally stable) to 1 (maximally unstable); it is a ratio of two counts, so it has no unit
Ce: efferent couplings: how many other packages this package depends on (imports), its outgoing arrows
Ca: afferent couplings: how many other packages depend on (import) this package, its incoming arrows
In words: instability is the fraction of a package's dependencies that point outwards. A package that only imports others and is imported by nobody scores 1; a package that is imported by others and imports nothing scores 0.
```

Martin's original definition counts *classes* on each side of the boundary (classes outside that depend on classes inside, and classes inside that depend on classes outside); counting whole packages or modules, as here, is a common simplification that can give different numbers, though the idea is the same. If a package has no dependencies in either direction, both counts are 0 and the formula becomes 0 divided by 0, which is undefined; tools pick their own convention for that case.

For example, suppose `billing` is imported by `orders` and `checkout`, and itself imports only `money`:

```formula
I = Ce / (Ca + Ce)
I = 1 / (2 + 1)
I ≈ 0.33
where
I: the instability of `billing`, from 0 to 1, no unit
Ce: packages `billing` imports: only `money`, so 1
Ca: packages that import `billing`: `orders` and `checkout`, so 2
≈: approximately equal to (one third, rounded to two decimal places)
In words: one of billing's three dependency arrows points outwards, so it is fairly stable: two packages would feel any change to it.
```

A web package that imports four others and is imported by nothing has instability one; a `money` package imported by four others that imports nothing has instability zero.

Volatile code (UI, integrations, experiments) should have high *I* and depend on low-*I* code, never the other way round. If a stable core package imports a volatile one, every experiment risks breaking the core.

The related **Stable Abstractions Principle** says stable packages should be abstract (interfaces or abstract types; a pure calculation is not automatically abstract) so they can be extended without being modified. That is why ports, owned by the core, sit at the stable end.

## Key takeaways
- Dependency cycles increase coupling and hinder independent reasoning.
- Stable means costly to change because other code depends on it.
- Instability is outgoing dependencies divided by all incoming and outgoing dependencies.
- Counting whole packages is a stated simplification of Martin’s original class counts.
- An isolated package gives an undefined zero-over-zero ratio unless a tool defines a convention.

## Further reading
- [OO Design Quality Metrics — Robert C. Martin](https://condor.depaul.edu/dmumaugh/OOT/Design-Principles/oodmetrc.pdf)
