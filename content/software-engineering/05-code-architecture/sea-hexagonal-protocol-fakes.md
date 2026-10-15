---
id: sea-hexagonal-protocol-fakes
sourceLesson: sea-hexagonal
title: Protocols, repositories and fake adapters
level: intermediate
minutes: 5
summary: Trace a Python use case through structural ports and verify behavior with in-memory fakes.
---

The core owns interfaces and external adapters satisfy them. This unit builds that arrangement in Python, sharing definitions between fragments as noted below.

## A Python example

The core defines ports with typing.Protocol for static structural typing: matching member types can satisfy the contract without inheritance. Type hints do not enforce the behavioral contract at runtime. These snippets share their definitions; a packaged app needs the corresponding imports.

```python
# core/model.py
class Order:
    def __init__(self, oid, status):
        self.id = oid
        self.status = status

    def place(self):
        if self.status != "draft":
            raise ValueError("not draft")
        # Record the valid state transition.
        self.status = "placed"
```

```python
# core/ports.py
from typing import Protocol

class OrderRepository(Protocol):
    def get(self, oid: int) -> "Order":
        ...
    def add(self, order: "Order") -> None:
        ...

class Notifier(Protocol):
    def order_placed(self, order) -> None:
        ...
```

The use case depends only on those ports. This minimal example demonstrates wiring, not reliable cross-system delivery: saving and notifying need an explicit transaction/retry policy. A production flow can save the state and an outbox row in one database commit, then notify asynchronously.

```python
# core/services.py
class PlaceOrder:
    def __init__(self,
                 repo: OrderRepository,
                 notify: Notifier):
        self.repo = repo
        self.notify = notify

    def __call__(self, oid: int) -> None:
        order = self.repo.get(oid)
        order.place()
        # Persistence and notification are
        # separate effects in this demo.
        self.repo.add(order)
        self.notify.order_placed(order)
```

Driven adapters live outside the core and import it:

```python
# adapters/sql_repo.py
from core.model import Order

class SqlOrderRepository:
    def __init__(self, session):
        self.s = session

    def get(self, oid):
        row = self.s.get(OrderRow, oid)
        if row is None:
            raise LookupError(oid)
        return Order(row.id, row.status)

    def add(self, order):
        row = self.s.get(OrderRow, order.id)
        if row is None:
            raise LookupError(order.id)
        # Copy domain state into the ORM
        # row.
        row.status = order.status
```

The SQL fragment assumes an OrderRow mapping and a caller-owned session transaction. Here add updates an existing row; it is not a general insert implementation. Notice the translation: `OrderRow` is an ORM class, `Order` is a plain domain class, and the adapter maps between them. ORM types never cross the port.

For tests, a second adapter fits the same port in memory:

```python
# tests/fakes.py
class FakeRepo:
    def __init__(self, orders):
        # Keep references, not detached
        # copies.
        self.orders = {o.id: o
                       for o in orders}
    def get(self, oid):
        return self.orders[oid]
    def add(self, order):
        self.orders[order.id] = order

class FakeNotifier:
    def __init__(self):
        self.sent = []
    def order_placed(self, order):
        # Record the observable
        # notification.
        self.sent.append(order.id)
```

```python
def test_place_order_notifies():
    repo = FakeRepo([Order(1, "draft")])
    notifier = FakeNotifier()
    PlaceOrder(repo, notifier)(1)
    # Verify saved state and sent order id.
    assert repo.get(1).status == "placed"
    assert notifier.sent == [1]
```

That test requires no database, network or mock library.

> [!note] Evidence gap
> No fixed test-duration figure is asserted without a measured environment. Fake-based tests also need adapter contract/integration checks; they do not prove real transaction, missing-row or concurrency behavior. Fakes like these are often more robust than mocks, because they check *behaviour* (what ended up stored) rather than *which methods were called*.

## Key takeaways
- A Protocol checks compatible member types statically; type hints alone do not enforce behavior.
- Adapters map database rows to plain domain objects.
- Fakes let core tests inspect results without a database or network.
- Real adapters still need integration and contract checks, including transaction behavior.

## Further reading
- [PEP 544 — Protocols: structural subtyping](https://peps.python.org/pep-0544/)
- [Architecture Patterns with Python: Repository Pattern](https://www.cosmicpython.com/book/chapter_02_repository.html)
