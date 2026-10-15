---
id: sea-layer-discount-flow
sourceLesson: sea-layered
title: A discount use case across layers
level: basic
minutes: 4
summary: Follow one discount request through a domain rule, repository, application service and HTTP translator.
---

The previous unit mixed HTTP, pricing and SQL in one view. These connected teaching fragments separate those concerns; they are not a complete web application.

The following teaching fragments split the feature into layers; module imports and app wiring are omitted. Assume decimal totals are stored as text in the SQLite example. A real endpoint also needs authorization, input validation, an explicit transaction/concurrency policy and a decision about repeated discount requests.

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
> The repository builds `Order` objects, so `data` imports `domain`, an arrow pointing *up* the diagram. That conflicts with a literal source-import ordering of this particular diagram. Layered separation can use mappers or dependency inversion; it does not require domain objects to inherit an ORM. The ports-and-adapters units develop dependency inversion explicitly.

> [!note] Application layer vs domain layer
> The domain holds rules that would exist even without software: "a closed order can't be discounted". The application layer orchestrates a use case: load, call the domain, save, finish with a database commit, perhaps send an email. Fowler calls the latter a **service layer**. In a rich domain-model design, repeated business decisions in application services suggest missing domain behavior. Conditional orchestration is not itself a violation, and transaction-script designs deliberately organize logic differently.

## Key takeaways
- The domain owns discount eligibility and valid percentage rules.
- The application orchestrates loading, domain behavior and saving.
- Views translate errors to HTTP; production transactions and authorization need explicit policies.
- A repository importing a domain object needs an import ordering compatible with that dependency.

## Further reading
- [Service Layer — Martin Fowler](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- [Architecture Patterns with Python: Service Layer](https://www.cosmicpython.com/book/chapter_04_service_layer.html)
