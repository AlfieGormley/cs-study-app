---
id: sea-ddd-events-contexts
sourceLesson: sea-ddd
title: Events, bounded contexts and translation
level: intermediate
minutes: 5
summary: Coordinate separate aggregates explicitly and translate between models at bounded-context edges.
---

The preceding unit protects one aggregate at a time. Rules that cross those boundaries need an explicit consistency choice; model boundaries also need explicit translation. The Customer example from the first DDD unit is reused below.

### Rules across aggregates: cross-aggregate eventual consistency

What about "reserve stock when an order is placed"? Stock is a different aggregate (maybe a different context). Rather than updating both in one transaction, `Order.place()` records an `OrderPlaced` **domain event**. Save the state and a durable pending event in one database commit (for example an outbox); a reliable relay invokes an idempotent reservation handler in a separate transaction. If reservation fails, a compensating action (cancel the order, notify the customer) follows.

This is a deliberate trade: big aggregates give immediate consistency but more lock contention and slower loads; small ones scale but need event handling.

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

A context is a *model* boundary. It might be a module in a monolith, a separate service or a separate team's codebase. One team typically owns one or more contexts, and communication structure can influence boundaries; Conway's observation is not a deterministic rule that contexts must match teams.

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

## Key takeaways
- A domain event records a meaningful fact that another transaction can handle.
- An outbox couples durable event recording with the state commit; handlers still need idempotency and failure handling.
- Bounded contexts allow one business word to have different local models.
- An anti-corruption layer translates an external model into the local language.
- Immediate cross-aggregate invariants may require a different owner, reservations or a deliberate atomic transaction.

## Further reading
- [Domain-Driven Design Reference — Eric Evans](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf)
- [Bounded Context — Martin Fowler](https://martinfowler.com/bliki/BoundedContext.html)
- [Transactional outbox — Chris Richardson](https://microservices.io/patterns/data/transactional-outbox.html)
- [Anti-corruption Layer — Azure](https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer)
