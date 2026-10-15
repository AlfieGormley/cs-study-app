---
id: sep-instability-tradeoffs
title: Measure dependency direction without overreading it
level: intermediate
minutes: 4
summary: Instability is the outgoing share of incoming and outgoing dependency links.
sourceLesson: sep-coupling-cohesion
---

Coupling concerns dependencies across a boundary; cohesion concerns the responsibilities grouped inside it. Use both when considering a design change.

## Measuring it

A module-level variant of Robert C. Martin's package metrics gives a rough number. Here we count distinct modules (other formulations count classes across package boundaries). Start with two counts for a module:

- **Afferent coupling**: how many other modules depend on it (incoming dependencies). "Afferent" means "carried towards".
- **Efferent coupling**: how many other modules it depends on (outgoing dependencies). "Efferent" means "carried away".

**Instability** combines them into one number: the share of a module's dependency links that point outwards. Use it to ask "if I change this module, how many others might break?" and "how exposed is it to changes elsewhere?"

```formula
I = Ce / (Ca + Ce)
where
I: the module's instability, a plain ratio with no unit, from 0 (maximally stable) to 1 (maximally unstable)
Ce: efferent coupling, the number of other modules this module depends on (outgoing)
Ca: afferent coupling, the number of other modules that depend on this module (incoming)
In words: instability is outgoing dependencies divided by all dependencies, in either direction. The more a module leans on others, and the fewer lean on it, the closer it is to 1.
```

A worked example. A `money` module is imported by 9 other modules and imports only 1 itself. An `admin_report` module is imported by nothing and imports 4 modules:

```formula
I_money = 1 / (9 + 1) = 0.1
I_report = 4 / (0 + 4) = 1
where
I_money: the instability of the money module, a ratio with no unit
I_report: the instability of the admin_report module, a ratio with no unit
In words: money has 9 incoming and 1 outgoing link, so it is very stable (0.1); admin_report has only outgoing links, so it is maximally unstable (1).
```

A module that many others use and that depends on little (an instability near zero, like `money`) has many potential callers to affect when its contract changes. Keep that contract deliberate and stable; the metric alone does not prove that every such module must be abstract. A value near one means outgoing dependencies dominate, not that nobody depends on it. Exactly one means there are outgoing dependencies and no incoming ones, as with `admin_report`.

Limits of the metric:

- It needs a positive total number of incoming and outgoing dependencies. An isolated module (no links either way) divides 0 by 0, so its instability is undefined unless a tool specifies a convention.
- Every dependency counts as 1, whether it uses one function or fifty.
- The ratio measures structural dependence, not observed change frequency.

The **stable dependencies principle** says dependencies should point towards stability: a module should depend only on modules whose instability is lower than its own.

## Trade-offs

- **Decoupling has a price.** Every interface, event bus or message queue added to cut a dependency is something to understand and debug. An event fired into the void is loosely coupled and very hard to trace.
- **Coupling to stable things is cheap.** Depending on documented Python standard-library APIs is coupling to compatibility commitments; releases can still deprecate or remove APIs.
- **Distributed coupling is the worst kind.** Two microservices that must deploy together are tightly coupled *and* separated by a network. That is the "distributed monolith".
- **Cohesion is contextual.** Grouping by technical layer (`models/`, `views/`) is logical cohesion; grouping by feature (`billing/`, `search/`) is usually more functional. Neither is wrong everywhere.

## Key takeaways
- Instability is the outgoing share of incoming and outgoing dependency links.
- No links means an undefined ratio unless a tool adopts a convention.
- Structural stability does not measure change frequency, and decoupling has an ongoing cost.

## Further reading
- [NDepend: code metrics](https://www.ndepend.com/docs/code-metrics#Instability)
- [coupling.pdf](https://martinfowler.com/ieeeSoftware/coupling.pdf)
