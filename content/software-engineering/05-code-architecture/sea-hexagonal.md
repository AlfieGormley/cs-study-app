---
id: sea-hexagonal
title: Hexagonal and clean architecture
level: intermediate
minutes: 13
summary: Ports and adapters, the dependency rule, how clean and onion architecture relate, a working Python example with fakes for testing, and when the extra indirection isn't worth it.
---

A conventional downward dependency from domain to infrastructure couples business code to storage; layered separation can instead use dependency inversion. In 2005 Alistair Cockburn proposed a different picture. Put the application in the **middle**, and treat the database, the web UI, the test suite and the message queue as interchangeable things plugged in around the edge.

He called it **hexagonal architecture**, or more descriptively **ports and adapters**. The hexagon shape has no meaning; it just gave him room to draw several ports.

## The picture

```
          HTTP      CLI      tests
            \        |        /
        [adapter][adapter][adapter]
             \       |       /
          +---- driving ports ----+
          |                       |
          |   application core    |
          |   (use cases +        |
          |    domain model)      |
          |                       |
          +---- driven ports -----+
             /       |       \
        [adapter][adapter][adapter]
            /        |        \
       Postgres    SMTP    payment API
```

- The **core** holds the domain model and the use cases. It imports no framework, driver or SDK.
- A **port** is an interface the core defines, in its own terms.
- An **adapter** converts between a port and some specific technology.

There are two kinds of port:

| Kind | Who calls whom | Examples |
|---|---|---|
| Driving (primary) | Outside calls core | Use case API |
| Driven (secondary) | Core calls outside | Repository, mailer |

A Flask view is a **driving adapter**: it turns an HTTP request into a call on the core. A Postgres repository is a **driven adapter**: it implements a port the core needs.

## The trick: dependency inversion

The core *calls* the database, but it must not *import* the database code. The way out is the dependency inversion principle (the D in SOLID): the core owns an abstract interface, and the adapter depends on that interface.

```
 Classic:     domain ---> SqlRepo
 Hexagonal:   domain ---> OrderRepo (port)
                              ^
                              |  implements
                           SqlRepo (adapter)
```

The runtime call still goes from core to database. The *source code* dependency now points inwards. That is the whole idea.

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

The use case depends only on those ports. This minimal example demonstrates wiring, not reliable cross-system delivery: saving and notifying need an explicit transaction/retry policy. A production flow can atomically commit state and an outbox row, then notify asynchronously.

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
        row.status = order.status
```

The SQL fragment assumes an OrderRow mapping and a caller-owned session transaction. Here add updates an existing row; it is not a general insert implementation. Notice the translation: `OrderRow` is an ORM class, `Order` is a plain domain class, and the adapter maps between them. ORM types never cross the port.

For tests, a second adapter fits the same port in memory:

```python
# tests/fakes.py
class FakeRepo:
    def __init__(self, orders):
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
        self.sent.append(order.id)
```

```python
def test_place_order_notifies():
    repo = FakeRepo([Order(1, "draft")])
    notifier = FakeNotifier()
    PlaceOrder(repo, notifier)(1)
    assert repo.get(1).status == "placed"
    assert notifier.sent == [1]
```

That test requires no database, network or mock library.

> [!note] Evidence gap
> No fixed test-duration figure is asserted without a measured environment. Fake-based tests also need adapter contract/integration checks; they do not prove real transaction, missing-row or concurrency behavior. Fakes like these are often more robust than mocks, because they check *behaviour* (what ended up stored) rather than *which methods were called*.

## The composition root

Something has to choose which adapters to plug in. That place is the **composition root**, usually the entry point (`main.py`, the app factory, or a `bootstrap.py`). It coordinates concrete wiring; this does not literally require one module to import every class in a large application.

```python
# bootstrap.py
def build_app(settings):
    session = make_session(settings.db_url)
    repo = SqlOrderRepository(session)
    notify = SmtpNotifier(settings.smtp)
    place = PlaceOrder(repo, notify)
    return make_flask_app(place)
```

This example does not need a dependency-injection framework. Passing objects to constructors, as here, is dependency injection.

## Clean and onion architecture

Two later variants describe the same idea with concentric circles.

- **Onion architecture** (Jeffrey Palermo, 2008): domain model in the centre, then domain services, then application services, with UI, infrastructure and tests in the outer ring.
- **Clean architecture** (Robert C. Martin, 2012): entities in the centre, then use cases, then interface adapters (controllers, presenters, gateways), then frameworks and drivers.

```
 +----------------------------------+
 | frameworks & drivers (web, DB)   |
 | +------------------------------+ |
 | | interface adapters           | |
 | | +--------------------------+ | |
 | | | use cases                | | |
 | | | +----------------------+ | | |
 | | | | entities             | | | |
 | | | +----------------------+ | | |
 | | +--------------------------+ | |
 | +------------------------------+ |
 +----------------------------------+
   source dependencies point inwards
```

Martin states the **Dependency Rule**: source code dependencies can only point inwards. Nothing in an inner circle may name anything in an outer one: no function, class, variable or data format.

| Name | Centre | Emphasis |
|---|---|---|
| Hexagonal | App core | Ports per purpose |
| Onion | Domain model | Domain rings |
| Clean | Entities | Use-case layer |

The differences are mostly vocabulary. All three keep business logic independent of frameworks, UI and storage, and all three get there by inverting dependencies at the boundary.

> [!note] Data crossing boundaries
> Clean architecture also says that data passed across a boundary should be in the form most convenient for the *inner* circle. Don't pass an ORM row or a Flask `Request` into a use case. In Martin's stated boundary rule, pass simple values or dedicated data-transfer structures, not entities or database rows. The repository example above illustrates ports and adapters; it does not implement every Clean Architecture boundary prescription.

## Real-world use

- *Architecture Patterns with Python* (Percival and Gregory, also free online as "Cosmic Python") builds a Flask and SQLAlchemy app this way, with repositories, a unit of work, a service layer and a message bus.
- In its [2020 studio case study](https://netflixtechblog.com/ready-for-changes-with-hexagonal-architecture-b315ec967749), Netflix described moving a read from a JSON service to a GraphQL source through a new adapter. The sources held equivalent synchronized data; this case does not prove arbitrary providers are interchangeable.
- Many Java teams use Spring with a hexagonal package layout, sometimes enforced with ArchUnit; Python teams use `import-linter`.

## Trade-offs

What you gain:

- **Testability**: fast tests of business rules with in-memory fakes.
- **Replaceability**: an adapter can isolate a provider change when its semantics satisfy the existing port; transactions, consistency and capabilities may still require design changes.
- **Deferrable decisions**: you can build and test the core before choosing the database.
- **Clarity**: the core reads as a description of the business, not of the framework.

What it costs:

- **Mapping code**: domain objects and ORM rows are separate, so you write and maintain translations.
- **Indirection**: a reader follows a port to find the real implementation.
- **Lost framework conveniences**: Django admin and ModelForm are built around ORM models. Separate domain classes require mapping or integration, but do not inherently prevent retaining these framework features.

> [!warning] When not to bother
> A mostly-CRUD app (forms in, rows out, few rules) has little to protect. Ports and adapters would add mapping layers around almost no logic. Use the framework's defaults and extract a core only when real business rules appear.

## Common pitfalls

1. **Leaky ports.** A repository port that returns SQLAlchemy `Query` objects, or takes raw SQL fragments, has let the database back into the core.
2. **Ports shaped like tables.** `get_order_row()` and `update_order_status_column()` are storage operations, not domain needs. Ports should speak the core's language: `get(order_id)`, `add(order)`.
3. **An interface for everything.** You need ports at the boundary with the outside world (I/O, time, randomness, third parties). Pure domain classes calling each other don't need abstract interfaces between them.
4. **Mocking what you own, faking nothing.** If every test mocks the repository with `assert_called_with(...)`, tests break on harmless refactors. Prefer simple fakes.
5. **Logic in adapters.** A view that decides discounts, or a repository that silently filters cancelled orders, has moved policy out of the core.

## Key takeaways
- Hexagonal architecture puts the application core in the centre and treats UI, storage and external services as plug-in adapters.
- Ports are interfaces owned by the core; driving ports are called from outside, driven ports are implemented outside.
- Dependency inversion makes source dependencies point inwards even when calls go outwards.
- Clean and onion architecture are concentric-circle versions of the same idea, governed by the Dependency Rule.
- In-memory fake adapters give fast, behaviour-focused tests of business rules.
- The cost is mapping and indirection; skip it for thin CRUD apps.

## Further reading
- [Hexagonal Architecture — Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [The Clean Architecture — Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal architecture (software) — Wikipedia](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))
- [Architecture Patterns with Python: Repository Pattern](https://www.cosmicpython.com/book/chapter_02_repository.html)
- [Architecture Patterns with Python: Dependency Injection](https://www.cosmicpython.com/book/chapter_13_dependency_injection.html)
- [PEP 544 — Protocols: structural subtyping](https://peps.python.org/pep-0544/)
