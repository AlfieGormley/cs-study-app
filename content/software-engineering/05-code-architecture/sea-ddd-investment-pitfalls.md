---
id: sea-ddd-investment-pitfalls
sourceLesson: sea-ddd
title: Choosing where DDD earns its cost
level: intermediate
minutes: 4
summary: Distinguish core, supporting and generic subdomains and avoid mechanical modelling.
---

Domain modelling costs time and coordination. After learning entities, aggregates and bounded contexts, use subdomain categories to decide where that investment has the greatest value.

## Subdomains: where to spend effort

Evans separates the **core domain** from **generic subdomains**. Later writers add a third category in between; Vaughn Vernon's *Implementing Domain-Driven Design* (2013), for example, describes core, supporting and generic subdomains:

- **Core subdomain**: what makes the business distinctive (pricing for an insurer, routing for a logistics firm). Evans' advice is to keep it small, put your best people on it and spend your deepest modelling effort here.
- **Supporting subdomain**: needed and specific to this business, but not a differentiator (internal approval workflows).
- **Generic subdomain**: capabilities that do not differentiate this business. Evans suggests separating them and considering off-the-shelf solutions. Authentication or payments may be generic here but core to another business.

Full tactical DDD is expensive. It usually pays off in the core domain and is often overkill elsewhere.

> [!analogy] Real-world analogy: a specialty coffee roaster
> A small roaster's reputation rests on how it sources and roasts its beans, so the founders do that themselves and obsess over it. It runs wholesale orders on a simple in-house spreadsheet, and it pays staff with an off-the-shelf payroll service.
>
> **How it maps:** Roasting is the core subdomain, where expert attention creates the advantage. The order spreadsheet is a supporting subdomain: specific to this business, but good enough is fine. Payroll is generic: every business needs it, nobody chooses a roaster for its payroll, so buy it.
>
> **Where it stops:** A roaster can see at a glance which activity is its core. In software the line is often unclear and moves as the business changes, and something generic for one company (payments) is the core product of another.

## Pitfalls

1. **DDD as a pattern checklist.** Adding `Entity`, `ValueObject` and `AggregateRoot` base classes to a CRUD app without talking to domain experts gives you ceremony without insight.
2. **Giant aggregates.** With naive whole-graph loading and one shared root version, putting all orders, addresses and invoices inside Customer creates large loads and contention between unrelated changes.
3. **Object references between aggregates.** `order.customer.credit_limit -= x` modifies two aggregates in one transaction and breaks the boundary.
4. **One enterprise-wide model.** The canonical data model that tries to satisfy every department is the opposite of bounded contexts and tends to satisfy none.
5. **Public mutable collections.** Exposing `order.lines` as a list lets callers bypass `add_line` and its checks.

## Key takeaways
- Invest the richest modelling in the business’s core differentiator.
- Generic capabilities can often be bought or reused; classification depends on the business.
- Pattern checklists and giant aggregates add ceremony or contention.
- Separate bounded-context models and controlled aggregate mutations preserve useful boundaries.

## Further reading
- [Domain-Driven Design Reference — Eric Evans](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf)
- [DDD Aggregate — Martin Fowler](https://martinfowler.com/bliki/DDD_Aggregate.html)
- [Bounded Context — Martin Fowler](https://martinfowler.com/bliki/BoundedContext.html)
