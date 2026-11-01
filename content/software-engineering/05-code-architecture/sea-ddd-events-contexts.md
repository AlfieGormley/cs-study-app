---
id: sea-ddd-events-contexts
sourceLesson: sea-ddd
title: Events, bounded contexts and translation
level: intermediate
minutes: 5
summary: Coordinate separate aggregates explicitly and translate between models at bounded-context edges.
---

The preceding unit protects one aggregate at a time. This unit looks at two kinds of boundary beyond that: rules that cross aggregates, and whole models that meet at the edge of a bounded context. The `Customer` class from the first DDD unit is reused below.

### Rules across aggregates: cross-aggregate eventual consistency

What about "reserve stock when an order is placed"? Stock is a different aggregate (maybe a different context). Rather than updating both in one transaction, `Order.place()` records an `OrderPlaced` **domain event**: a fact that something meaningful happened.

To make sure the event isn't lost, save it in the same database commit as the order, for example as a row in an outbox table. A relay then delivers it to a stock-reservation handler, which runs in its own transaction. Delivery may repeat, so the handler must be idempotent: handling the same event twice must not reserve stock twice. If reservation fails, a compensating action follows, such as cancelling the order and telling the customer.

This is a deliberate trade. One big aggregate gives immediate consistency but more lock contention and slower loads. Small aggregates linked by events scale better, but for a while the order is placed and the stock not yet reserved, and you must handle failures.

## Bounded contexts

A big business does not have one model of "customer". Sales thinks of leads, contacts and deal value. Billing thinks of payment methods and invoices. Support thinks of tickets and service level. Forcing all of these into one `Customer` class produces a 90-field monster nobody understands.

A **bounded context** is a boundary within which one model and one language apply consistently. The same word can mean different things in different contexts, and that is fine.

```
 +---- Sales ----+     +--- Billing ----+
 | Customer:     |     | Account:       |
 |  lead score   |     |  payment card  |
 |  deal stage   |     |  invoices      |
 +---------------+     +----------------+
          \                  /
           shared: customer id
```

A context is a *model* boundary. It might be a module in a monolith, a separate service or a separate team's codebase. Usually one team owns one or more contexts. How teams communicate tends to shape where boundaries end up (Conway's law, covered at the end of this module), but it's a tendency, not a rule that contexts must match teams.

### Context mapping

How contexts relate is as important as what's inside them. Evans' common relationship patterns:

| Pattern | Meaning |
|---|---|
| Shared kernel | Two teams share a small model |
| Customer/supplier | Upstream serves downstream needs |
| Conformist | Downstream adopts upstream as-is |
| Anti-corruption layer | Downstream translates upstream |
| Open host service | Upstream offers a public protocol |
| Published language | A documented shared format |

The **anti-corruption layer** (ACL) is useful when an external model should not shape your own. When your context consumes a legacy system or a third party with a messy model, you put a translation layer at your context's boundary so their concepts never leak into your model:

```python
class LegacyCrmAdapter:
    """ACL: CRM records -> our Customer."""

    def __init__(self, client):
        self.client = client

    def get(self, cid):
        # Keep legacy names at this
        # boundary.
        rec = self.client.fetch(cid)
        return Customer(
            customer_id=rec["CUST_NO"],
            name=rec["NM_FULL"],
        )
```

That's the hexagonal driven adapter again, with an explicit job of keeping the model clean.

> [!analogy] Real-world analogy: a hospital admissions desk
> A hospital receives referral letters from dozens of family doctors' practices, each with its own layout, abbreviations and codes. The admissions desk copies what matters onto the hospital's own admission form. The wards only ever see that one form.
>
> **How it maps:** Each practice's letter format is an upstream model you don't control. The admissions desk is the anti-corruption layer, the hospital form is your domain model, and the wards are the rest of your code, which never learns the practices' quirks.
>
> **Where it stops:** A clerk can ring the practice when a letter is unclear. An ACL has to have explicit rules for every code it meets, including what to do with a value it can't map, and it must be updated whenever the upstream system changes its format.

## Key takeaways
- A domain event records a meaningful fact that another transaction can handle.
- An outbox records the event in the same database commit as the state change; handlers still need idempotency and failure handling.
- Bounded contexts allow one business word to have different local models.
- An anti-corruption layer translates an external model into the local language.
- Immediate cross-aggregate invariants may require a different owner, reservations or a deliberate atomic transaction.

## Further reading
- [Domain-Driven Design Reference — Eric Evans](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf)
- [Bounded Context — Martin Fowler](https://martinfowler.com/bliki/BoundedContext.html)
- [Transactional outbox — Chris Richardson](https://microservices.io/patterns/data/transactional-outbox.html)
- [Anti-corruption Layer — Azure](https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer)
