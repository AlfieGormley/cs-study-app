---
id: sea-layered
title: Layered architecture
level: basic
minutes: 11
summary: Splitting an application into presentation, application, domain and data layers, the one rule that makes layering work, and the ways it goes wrong in practice.
---

Open a small web app written in a hurry and you often find one function that parses the HTTP request, checks the user's permissions, applies a discount rule, writes SQL and formats the JSON response. It works. Then someone asks for the same discount rule in a nightly batch job, and there is no way to call it without faking an HTTP request.

**Layered architecture** is a common answer to this. You split the code by *kind of concern* into horizontal layers, and you only let each layer talk to the ones beneath it.

## The classic layers

Most descriptions use three or four layers. Martin Fowler's *presentation, domain, data* split is the core; many teams add an **application** (or service) layer between presentation and domain.

```
 +--------------------------------+
 | Presentation                   |
 | HTTP views, CLI, templates     |
 +--------------------------------+
 | Application / service          |
 | use cases, transactions, auth  |
 +--------------------------------+
 | Domain                         |
 | business rules and concepts    |
 +--------------------------------+
 | Data / infrastructure          |
 | SQL, ORM, files, external APIs |
 +--------------------------------+
   calls go downwards only
```

| Layer | Answers | Knows nothing about |
|---|---|---|
| Presentation | How do users talk to us? | SQL, tables |
| Application | What can users do? | HTTP, JSON |
| Domain | What are the rules? | HTTP, storage |
| Data | Where is it stored? | Who called |

The point of the split is that each layer changes for a different reason. A redesign of the JSON format touches presentation. A new VAT rule touches the domain. Moving from MySQL to Postgres touches data. Separating those concerns can reduce the scope of changes; new requirements or storage semantics can still cross boundaries.

## The one rule: dependencies point down

A layer may depend on the layers below it, never above. The domain never imports a Flask request; the data layer never decides how a discount works.

Here is the tangled version first:

```python
@app.post("/orders/<int:oid>/discount")
def apply_discount(oid):
    code = request.json["code"]
    row = db.execute(
        "SELECT total, status FROM orders"
        " WHERE id = ?", (oid,)).fetchone()
    if row["status"] != "open":
        return {"error": "closed"}, 409
    if code == "SPRING10":
        new = row["total"] * 0.9
    db.execute(
        "UPDATE orders SET total = ?"
        " WHERE id = ?", (new, oid))
    return {"total": new}
```

There are several problems here. The discount rule lives in a view, so the batch job can't reuse it. Testing it needs a web client and a database. An unknown code even crashes with `UnboundLocalError`, because `new` is never assigned. And money is stored as a float.

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
        pct = Decimal(str(pct))
        if not pct.is_finite():
            raise ValueError("nonfinite")
        if not 0 <= pct <= 100:
            raise ValueError("range")
        factor = 1 - pct / 100
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
        if r is None:
            raise OrderNotFound(oid)
        return Order(r[0], Decimal(r[1]),
                     r[2])

    def save(self, order):
        self.conn.execute(
            "UPDATE orders SET total = ?"
            " WHERE id = ?",
            (str(order.total), order.id))
```

```python
# application/services.py
CODES = {"SPRING10": 10}

class UnknownCode(Exception):
    pass

def apply_discount(repo, oid, code):
    pct = CODES.get(code)
    if pct is None:
        raise UnknownCode(code)
    order = repo.get(oid)
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
> The repository builds `Order` objects, so `data` imports `domain`, an arrow pointing *up* the diagram. That conflicts with a literal source-import ordering of this particular diagram. Layered separation can use mappers or dependency inversion; it does not require domain objects to inherit an ORM. The next lesson develops dependency inversion explicitly.

> [!note] Application layer vs domain layer
> The domain holds rules that would exist even without software: "a closed order can't be discounted". The application layer orchestrates a use case: load, call the domain, save, commit, perhaps send an email. Fowler calls the latter a **service layer**. In a rich domain-model design, repeated business decisions in application services suggest missing domain behavior. Conditional orchestration is not itself a violation, and transaction-script designs deliberately organize logic differently.

## Strict vs relaxed layering

In **strict** (closed) layering, each layer may only call the one directly below. In **relaxed** (open) layering, a layer may skip down several levels, for example a view reading from the data layer directly for a simple report.

| Style | Benefit | Cost |
|---|---|---|
| Strict | Each layer fully hides the one below | Boilerplate pass-through code |
| Relaxed | Less ceremony | More places depend on low layers |

Strict layering can produce **architecture sinkhole** paths: requests that fall straight through every layer with no logic added. A `get_user` view calls `UserService.get_user`, which calls `UserRepository.get_user`, which runs one query. A few sinkhole paths are fine. If most requests look like this, the layers are adding ceremony rather than value, and a relaxed rule (or a simpler design) is better.

## Where layering is used

- **Django** apps blur presentation and data: models are ORM classes and usually hold domain logic too ("fat models"). Many teams add a `services.py` module per app as an application layer.
- **Rails** follows a similar Active Record style.
- **Java enterprise** stacks (Spring) commonly use controller, service and repository layers, almost exactly the diagram above.
- **Network stacks** (the OSI and TCP/IP models) and operating systems are layered in the same spirit: they illustrate layered responsibilities, although real implementations include cross-layer interactions and do not all follow this exact import rule.

## How layering goes wrong

### The database becomes the centre

In the classic diagram the data layer is at the bottom, and a literal downward dependency implementation couples the domain to storage. This is not inevitable in every layered design. In practice this means domain classes import the ORM, inherit from `models.Model` and are shaped like tables. Changing storage or testing the rules without a database becomes hard.

This is the weakness that hexagonal and clean architecture (next lesson) fix by inverting the dependency: the domain defines the interface it needs, and the data layer implements it.

### The anaemic domain

When layers are introduced mechanically, the domain classes often end up as bags of fields with getters and setters, and all logic moves into services. Fowler calls this the **anaemic domain model**. You pay for the layers but get procedural code with extra steps.

### Changes cut across every layer

Most feature work is *vertical*: "add a gift message to orders" touches the view, the service, the domain and the table. If the code is packaged by layer, one feature means edits in four distant folders.

```
 by layer            by feature
 views/              orders/
   orders.py           views.py
   users.py            services.py
 services/             model.py
   orders.py           repo.py
   users.py          users/
 repos/                views.py
   orders.py           ...
   users.py
```

**Package by feature** (sometimes called vertical slices) keeps the layers *inside* each feature folder. You still get the dependency rule, but related code sits together, which is high cohesion. Lesson 4 of this module returns to this.

> [!tip] Rule of thumb
> Layers are about dependency direction, not folder names. You can have one file with clearly separated functions that respect the rule, or ten folders that violate it. Check the imports, not the tree.

## Enforcing the rule

Conventions decay unless something checks them. In Python, `import-linter` can fail the build when a lower layer imports a higher one:

```ini
[importlinter]
root_package = shop

[importlinter:contract:layers]
name = Layered architecture
type = layers
layers =
    shop.presentation
    shop.application
    shop.data
    shop.domain
```

The `layers` contract lists layers top to bottom and forbids any import from a lower layer to a higher one. Higher layers importing lower ones is allowed, whether or not they skip a level. Notice that `domain` is listed *last* here, below `data`, so the repository may import `Order` but `Order` may never import SQL code. Many Python teams end up with this order, which is already the hexagonal idea in disguise.

## Key takeaways
- Layers group code by kind of concern so each layer changes for a different reason.
- The rule that matters: dependencies point down. Lower layers never import higher ones.
- The application layer orchestrates use cases; the domain layer holds the business rules.
- Strict layering risks sinkhole pass-through code; relaxed layering trades isolation for less ceremony.
- A downward source dependency on infrastructure couples rules to storage; dependency inversion can preserve layered separation without that coupling.
- Package by feature with layers inside each feature often beats top-level folders per layer.

## Further reading
- [Presentation Domain Data Layering — Martin Fowler](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)
- [Service Layer — Patterns of Enterprise Application Architecture](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- [Anemic Domain Model — Martin Fowler](https://martinfowler.com/bliki/AnemicDomainModel.html)
- [Multitier architecture — Wikipedia](https://en.wikipedia.org/wiki/Multitier_architecture)
- [Import Linter documentation](https://import-linter.readthedocs.io/en/stable/)
- [Architecture Patterns with Python: Service Layer](https://www.cosmicpython.com/book/chapter_04_service_layer.html)
