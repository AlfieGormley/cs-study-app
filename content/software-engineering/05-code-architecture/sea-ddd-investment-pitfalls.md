---
id: sea-ddd-investment-pitfalls
sourceLesson: sea-ddd
title: Choosing where DDD earns its cost
level: intermediate
minutes: 3
summary: Distinguish core, supporting and generic subdomains and avoid mechanical modelling.
---

Domain modelling costs time and coordination. After learning entities, aggregates and bounded contexts, use subdomain categories to decide where that investment has the greatest value.

## Subdomains: where to spend effort

Evans also distinguishes kinds of subdomain:

- **Core subdomain**: what makes the business distinctive (pricing for an insurer, routing for a logistics firm). Invest your best people and richest modelling here.
- **Supporting subdomain**: needed and specific, but not a differentiator (internal approval workflows).
- **Generic subdomain**: capabilities that do not differentiate this business and can be bought or reused. Authentication or payments may be generic here but core to another business.

Full tactical DDD is expensive. It pays off in the core domain and is usually overkill elsewhere.

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
