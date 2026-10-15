---
id: sea-ddd-aggregate-invariants
sourceLesson: sea-ddd
title: Aggregate roots and concurrent updates
level: intermediate
minutes: 5
summary: Protect an aggregate’s rules through its root and use optimistic locking to detect concurrent changes.
---

Entities and value objects describe individual concepts. An aggregate adds a boundary around the objects whose rules must hold together. The Money value object and dataclass import come from the preceding unit.

## Aggregates: consistency boundaries

Some rules involve several objects at once: "an order can have at most 50 lines". Customer-wide credit is a separate cross-order invariant unless the model explicitly includes credit reservations. An **aggregate** is a cluster of entities and values treated as one unit for changes, with a single **aggregate root** that outsiders talk to.

```
 +--------- Order aggregate ----------+
 |  Order (root)                      |
 |   id, status, version              |
 |   +----------+  +----------+       |
 |   |OrderLine |  |OrderLine |  ...  |
 |   +----------+  +----------+       |
 |   shipping: Address (value)        |
 +------------------------------------+
   outsiders hold Order.id only
```

The rules:

1. **Only the root is referenced from outside.** Code calls `order.add_line(...)`, never `order.lines.append(...)`. The root enforces the invariants.
2. **One aggregate, one transaction.** A common DDD guideline is to modify one aggregate per transaction; consciously chosen exceptions exist, and required invariants still need a correct atomic protocol. That aggregate is the unit of consistency and of locking.
3. **Reference other aggregates by id.** `Order` holds `customer_id`, not a `Customer` object, so loading an order need not traverse the customer graph; code must still deliberately respect transaction boundaries.
4. **Keep aggregates small.** Vaughn Vernon's advice: design small aggregates, and include something only if a rule demands it be consistent *immediately*.

```python
class OrderLocked(Exception): pass
class TooManyLines(Exception): pass
class EmptyOrder(Exception): pass

@dataclass(frozen=True)
class OrderLine:
    sku: str
    qty: int
    price: Money

@dataclass(frozen=True)
class OrderPlaced:
    order_id: int

class Order:
    MAX = 50

    def __init__(self, oid, customer_id):
        self.id = oid
        self.customer_id = customer_id
        self._lines = []
        self.status = "draft"
        self.version = 0
        self.events = []

    def add_line(self, sku, qty, price):
        if self.status != "draft":
            raise OrderLocked(self.id)
        # Enforce the limit before mutation.
        if len(self._lines) >= Order.MAX:
            raise TooManyLines(self.id)
        # Reject bool as well as nonpositive
        # qty.
        if type(qty) is not int or qty <= 0:
            raise ValueError("positive qty")
        if not isinstance(price, Money):
            raise TypeError("Money only")
        self._lines.append(
            OrderLine(sku, qty, price))

    def place(self):
        if self.status != "draft":
            raise OrderLocked(self.id)
        if not self._lines:
            raise EmptyOrder(self.id)
        # Record the valid state transition.
        self.status = "placed"
        # Record intent; durable delivery
        # needs
        # an outbox in the saving
        # transaction.
        self.events.append(
            OrderPlaced(self.id))
```

There is **one repository per aggregate** (`OrderRepository`, not `OrderLineRepository`), so domain changes go through its consistency boundary; optimized queries or persistence need not literally hydrate and rewrite every row.

### Concurrency: the version number

If two requests load the same order and both add a line, one change could overwrite the other. The usual fix is **optimistic locking** on the aggregate root:

```sql
UPDATE orders
SET status = 'placed', version = 8
WHERE id = 42 AND version = 7;
-- 0 rows: stale version or missing row.
-- Reload and retry, or report a conflict.
```

Because the aggregate is the consistency boundary, one root version can protect child changes only if every writer checks/advances it and writes all related changes in one database commit.

## Key takeaways
- An aggregate groups objects that must obey immediate aggregate invariants.
- Outside callers change it through its root rather than mutable child collections.
- Small aggregates reduce unnecessary loading and contention.
- An optimistic locking check protects child writes only when every writer advances the root version atomically with them.

## Further reading
- [Domain-Driven Design Reference — Eric Evans](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf)
- [DDD Aggregate — Martin Fowler](https://martinfowler.com/bliki/DDD_Aggregate.html)
- [Cosmic Python: Aggregates and Consistency Boundaries](https://www.cosmicpython.com/book/chapter_07_aggregate.html)
