---
id: sea-ddd-aggregate-invariants
sourceLesson: sea-ddd
title: Aggregate roots and concurrent updates
level: intermediate
minutes: 5
summary: Protect an aggregate’s rules through its root and use optimistic locking to detect concurrent changes.
---

Entities and value objects describe individual concepts. An aggregate adds a boundary around the objects whose rules must hold together. The code below reuses `Money` and the dataclass import from the preceding unit.

## Aggregates: consistency boundaries

Some rules involve several objects at once: "an order can have at most 50 lines". An **aggregate** is a cluster of entities and values treated as one unit for changes, with a single **aggregate root** that outsiders talk to. A rule that spans many orders, such as a customer-wide credit limit, is *not* protected by one order aggregate; the next unit covers rules like that.

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
2. **One aggregate, one transaction.** A widely used guideline is to change one aggregate per transaction (in Fowler's summary, "transactions should not cross aggregate boundaries"), so the aggregate is the unit of consistency and of locking. Teams do break it deliberately, for example when a rule genuinely needs two aggregates to change together.
3. **Reference other aggregates by id.** `Order` holds `customer_id`, not a `Customer` object, so loading an order doesn't drag in the customer and it's harder to change both by accident.
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
        # Record the fact. Durable delivery
        # needs an outbox written in the
        # same transaction as the order.
        self.events.append(
            OrderPlaced(self.id))
```

There is **one repository per aggregate** (`OrderRepository`, not `OrderLineRepository`), so changes always go through the root and its checks. Behind that repository, the storage code can still load or write individual rows efficiently.

### Concurrency: the version number

If two requests load the same order and both add a line, one change could overwrite the other. The usual fix is **optimistic locking** on the aggregate root: each save says "only if nobody has saved since I loaded version 7".

```sql
UPDATE orders
SET status = 'placed', version = 8
WHERE id = 42 AND version = 7;
-- 0 rows: stale version or missing row.
-- Reload and retry, or report a conflict.
```

Because the aggregate is the consistency boundary, one version number on the root can protect the lines too. That only works if every writer checks and advances the root's version, and saves the line changes in the same database transaction.

> [!analogy] Real-world analogy: a wiki edit conflict
> Two people open the same Wikipedia article and start editing. The first saves. When the second presses save, the wiki notices that the article has changed since they opened it. If it can't reconcile the two edits itself, it shows an edit-conflict page instead of silently overwriting the first person's work.
>
> **How it maps:** The revision the editor started from is the `version` they loaded. Saving is the version-checked `UPDATE`, and the edit-conflict screen is the application seeing 0 rows updated. Nobody locks the article while you type, which is why this is called *optimistic*: conflicts are assumed to be rare and are detected at save time.
>
> **Where it stops:** The wiki sometimes merges the two edits for you, and otherwise shows both versions so you can merge them by hand. A version-checked `UPDATE` merges nothing; your code must reload the aggregate and decide whether to retry the change or report the conflict.

## Key takeaways
- An aggregate groups objects that must obey immediate aggregate invariants.
- Outside callers change it through its root rather than mutable child collections.
- Small aggregates reduce unnecessary loading and contention.
- An optimistic locking check detects a conflicting save; it protects the lines only when every writer advances the root version in the same transaction.

## Further reading
- [Domain-Driven Design Reference — Eric Evans](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf)
- [DDD Aggregate — Martin Fowler](https://martinfowler.com/bliki/DDD_Aggregate.html)
- [Cosmic Python: Aggregates and Consistency Boundaries](https://www.cosmicpython.com/book/chapter_07_aggregate.html)
