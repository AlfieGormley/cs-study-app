---
id: sea-layer-discount-flow
sourceLesson: sea-layered
title: A discount use case across layers
level: basic
minutes: 4
summary: Follow one discount request through a domain rule, repository, application service and HTTP translator.
---

The previous unit mixed HTTP, pricing and SQL in one view. The four fragments below split the same feature into layers. They are teaching fragments, not a complete web application: module imports and app wiring are left out, and totals are stored as decimal text in SQLite. A real endpoint would also need authorization, input validation, a transaction and concurrency policy, and a decision about what a repeated discount request should do.

```python
# domain/order.py
from decimal import Decimal

class OrderClosed(Exception):
    pass

class Order:
    def __init__(self, oid, total, status):
        self.id = oid
        self.total = total
        self.status = status

    def apply_discount(self, pct):
        if self.status != "open":
            raise OrderClosed(self.id)
        # Convert before validating the
        # range.
        pct = Decimal(str(pct))
        if not pct.is_finite():
            raise ValueError("nonfinite")
        if not 0 <= pct <= 100:
            raise ValueError("range")
        factor = 1 - pct / 100
        # Mutate only after validating pct.
        self.total *= factor
```

```python
# data/order_repo.py
class OrderNotFound(LookupError):
    pass

class SqlOrderRepository:
    def __init__(self, conn):
        self.conn = conn

    def get(self, oid):
        r = self.conn.execute(
            "SELECT id, total, status"
            " FROM orders WHERE id = ?",
            (oid,)).fetchone()
        # Missing rows become domain-facing
        # errors.
        if r is None:
            raise OrderNotFound(oid)
        return Order(r[0], Decimal(r[1]),
                     r[2])

    def save(self, order):
        self.conn.execute(
            "UPDATE orders SET total = ?"
            " WHERE id = ?",
            # Store exact decimal text.
            (str(order.total), order.id))
```

```python
# application/services.py
CODES = {"SPRING10": 10}

class UnknownCode(Exception):
    pass

def apply_discount(repo, oid, code):
    # Reject unknown codes before loading.
    pct = CODES.get(code)
    if pct is None:
        raise UnknownCode(code)
    order = repo.get(oid)
    # The domain enforces discount
    # eligibility.
    order.apply_discount(pct)
    repo.save(order)
    return order.total
```

```python
# presentation/views.py
@app.post("/orders/<int:oid>/discount")
def discount_view(oid):
    try:
        total = services.apply_discount(
            repo, oid, request.json["code"])
    # Translate domain failures into HTTP.
    except OrderClosed:
        return {"error": "closed"}, 409
    except UnknownCode:
        return {"error": "unknown"}, 400
    except OrderNotFound:
        return {"error": "not found"}, 404
    return {"total": str(total)}
```

Now the batch job calls `services.apply_discount` directly. The rule in `Order` can be tested with no database at all. The view is a thin translator between HTTP and a use case.

> [!warning] Spot the awkward arrow
> The repository builds `Order` objects, so `data` imports `domain`: an arrow pointing *up* the diagram from the previous unit. Teams usually resolve this in one of two ways. Some list the domain *below* data in their dependency rules, so the repository may import `Order` but `Order` never imports SQL (a later unit shows this with Import Linter). Others have the domain define a repository interface that the data layer implements, which is dependency inversion; the ports-and-adapters units develop that idea.

> [!note] Application layer vs domain layer
> The domain holds rules that would exist even without software: "a closed order can't be discounted". The application layer orchestrates a use case: load, call the domain, save, finish with a database commit, perhaps send an email. Fowler calls this a **service layer**. In a rich domain model, business decisions that keep appearing in application services suggest behaviour missing from the domain. An `if` in a service is not automatically wrong, though: deciding *which steps to run* is orchestration, and a transaction-script design deliberately keeps simple logic in procedures.

## Key takeaways
- The domain owns discount eligibility and valid percentage rules.
- The application orchestrates loading, domain behavior and saving.
- Views translate errors to HTTP; production transactions and authorization need explicit policies.
- A repository that builds domain objects makes data depend on the domain; the layer rules must allow that, or an interface must invert it.

## Further reading
- [Service Layer — Martin Fowler](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- [Architecture Patterns with Python: Service Layer](https://www.cosmicpython.com/book/chapter_04_service_layer.html)
