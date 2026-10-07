---
id: sea-ddd
title: Domain-driven design
level: intermediate
minutes: 15
summary: Ubiquitous language, entities and value objects, aggregates as consistency boundaries, domain events, bounded contexts and how they map onto each other.
---

Most hard software isn't hard because of the technology. It's hard because the *business* is complicated: insurance underwriting, freight scheduling, clinical trials. Eric Evans' 2003 book *Domain-Driven Design* argues that in such systems the most valuable design work is modelling the domain itself, in close collaboration with the people who understand it.

DDD has two halves:

- **Strategic design**: how to carve a large domain into parts (bounded contexts) and how those parts relate.
- **Tactical design**: building blocks for the model inside one part: entities, value objects, aggregates, domain events, repositories.

Teams often adopt the tactical patterns and skip the strategic ones. Strategic boundaries deserve explicit attention; using entity and repository classes alone does not establish a useful domain model.

## Ubiquitous language

The starting point is a shared vocabulary between developers and domain experts, used in conversation, documents *and code*. If the underwriters say "a policy is **bound**", the code says `policy.bind()`, not `policy.set_status(3)`.

When the code uses different words from the business, every conversation needs translation, and translation is where misunderstandings breed. A mismatch you can't resolve is often a sign that you're straddling two contexts (see below).

## Entities: identity that persists

An **entity** is defined by its identity, not its attributes. A customer who changes their name and address is still the same customer. Two customers with identical names are different people.

```python
class Customer:
    def __init__(self, customer_id, name):
        self.id = customer_id
        self.name = name

    def __eq__(self, other):
        return (isinstance(other, Customer)
                and other.id == self.id)

    # Mutable entities are unhashable here.
    __hash__ = None
```

Keep entity identifiers stable throughout their lifecycle. The example leaves entities unhashable so mutable attributes cannot corrupt set/dict membership. Entities can have a lifecycle: created, changed, perhaps archived.

## Value objects: defined by their values

A **value object** has no identity. Two equal Money values represent the same amount and currency. Physical notes can have distinct serial-number identities in a different model. Value objects should be **immutable**: to "change" one you make a new one.

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if not isinstance(
                self.amount, Decimal):
            raise TypeError("Decimal only")
        if not self.amount.is_finite():
            raise ValueError("nonfinite")
        if self.amount < 0:
            raise ValueError("negative")
        allowed = {"GBP", "USD"}
        if self.currency not in allowed:
            raise ValueError("currency")

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency != self.currency:
            raise ValueError("currency")
        total = self.amount + other.amount
        return Money(total, self.currency)
```

With default eq=True, dataclass generates field equality; combining it with frozen=True normally generates a hash. Frozen blocks ordinary attribute assignment but does not deeply freeze contained objects, and hashing requires hashable fields. This example deliberately supports only nonnegative GBP/USD amounts; other domains may need negative money values and different currency/rounding rules. So `Money(Decimal("5"), "GBP") == Money(Decimal("5"), "GBP")` is `True`.

Why bother? Value objects:

- **Validate once**: this example checks construction and same-currency addition. Currency conversion, rounding, context precision and business-specific limits still need explicit policies.
- **Remove primitive obsession**: `Email`, `Postcode` and `Quantity` say more than `str` and `int`.
- **Are safe to share**: immutable objects can't be changed behind your back.

> [!tip] Default to value objects
> Most concepts in a model are values: date ranges, addresses, amounts, coordinates. Make something an entity only when you genuinely need to track it as "the same thing" over time.

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
        if len(self._lines) >= Order.MAX:
            raise TooManyLines(self.id)
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
        self.status = "placed"
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

Because the aggregate is the consistency boundary, one root version can protect child changes only if every writer checks/advances it and commits all related changes atomically in the same transaction.

### Rules across aggregates: eventual consistency

What about "reserve stock when an order is placed"? Stock is a different aggregate (maybe a different context). Rather than updating both in one transaction, `Order.place()` records an `OrderPlaced` **domain event**. Commit the state and a durable pending event atomically (for example an outbox); a reliable relay invokes an idempotent reservation handler in a separate transaction. If reservation fails, a compensating action (cancel the order, notify the customer) follows.

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

The **anti-corruption layer** (ACL) is useful when an external model should not shape your own. When your context consumes a legacy system or a third party with a messy model, you put a translation layer at the edge so their concepts never leak into your model:

```python
class LegacyCrmAdapter:
    """ACL: CRM records -> our Customer."""

    def __init__(self, client):
        self.client = client

    def get(self, cid):
        rec = self.client.fetch(cid)
        return Customer(
            customer_id=rec["CUST_NO"],
            name=rec["NM_FULL"],
        )
```

That's the hexagonal driven adapter again, with an explicit job of keeping the model clean.

## Subdomains: where to spend effort

Evans also distinguishes kinds of subdomain:

- **Core**: what makes the business distinctive (pricing for an insurer, routing for a logistics firm). Invest your best people and richest modelling here.
- **Supporting**: needed and specific, but not a differentiator (internal approval workflows).
- **Generic**: capabilities that do not differentiate this business and can be bought or reused. Authentication or payments may be generic here but core to another business.

Full tactical DDD is expensive. It pays off in the core domain and is usually overkill elsewhere.

## Pitfalls

1. **DDD as a pattern checklist.** Adding `Entity`, `ValueObject` and `AggregateRoot` base classes to a CRUD app without talking to domain experts gives you ceremony without insight.
2. **Giant aggregates.** With naive whole-graph loading and one shared root version, putting all orders, addresses and invoices inside Customer creates large loads and contention between unrelated changes.
3. **Object references between aggregates.** `order.customer.credit_limit -= x` modifies two aggregates in one transaction and breaks the boundary.
4. **One enterprise-wide model.** The canonical data model that tries to satisfy every department is the opposite of bounded contexts and tends to satisfy none.
5. **Public mutable collections.** Exposing `order.lines` as a list lets callers bypass `add_line` and its checks.

## Key takeaways
- DDD focuses design effort on modelling a complex business domain with its experts, in a shared ubiquitous language.
- Entities have identity; value objects are immutable and compared by value. Prefer value objects.
- An aggregate is a consistency boundary with one root: change one per transaction, reference others by id, keep them small.
- Rules spanning aggregates need an explicit consistency design; reliable events and compensation suit some requirements, while strict invariants need atomic ownership, reservations or transactions.
- Bounded contexts let each part of the business have its own model; context maps and anti-corruption layers manage the edges.
- Spend tactical DDD effort on the core domain; buy or simplify generic ones.

## Further reading
- [Domain Driven Design — Martin Fowler](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Bounded Context — Martin Fowler](https://martinfowler.com/bliki/BoundedContext.html)
- [DDD Aggregate — Martin Fowler](https://martinfowler.com/bliki/DDD_Aggregate.html)
- [Value Object — Martin Fowler](https://martinfowler.com/bliki/ValueObject.html)
- [Architecture Patterns with Python: Aggregates and Consistency Boundaries](https://www.cosmicpython.com/book/chapter_07_aggregate.html)
- [Anti-corruption Layer pattern — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer)
- [Domain-driven design — Wikipedia](https://en.wikipedia.org/wiki/Domain-driven_design)
