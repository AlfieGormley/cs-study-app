---
id: sea-hexagonal-composition-clean
sourceLesson: sea-hexagonal
title: Composition roots and clean architecture
level: intermediate
minutes: 4
summary: Wire concrete adapters at the entry point and compare hexagonal, onion and clean boundaries.
---

The preceding Python core can run with real adapters or fakes. One outer entry point must choose the concrete objects; this also clarifies where clean architecture draws its rings.

## The composition root

Something has to choose which adapters to plug in. That place is the **composition root**, usually the entry point (`main.py`, the app factory, or a `bootstrap.py`). It coordinates concrete wiring; this does not literally require one module to import every class in a large application.

```python
# bootstrap.py
def build_app(settings):
    # Partial: factories/settings provided.
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

Martin states **the Dependency Rule**: source code dependencies can only point inwards. Nothing in an inner circle may name anything in an outer one: no function, class, variable or data format.

| Name | Centre | Emphasis |
|---|---|---|
| Hexagonal | App core | Ports per purpose |
| Onion | Domain model | Domain rings |
| Clean | Entities | Use-case layer |

The differences are mostly vocabulary. All three keep business logic independent of frameworks, UI and storage, and all three get there by inverting dependencies at the boundary.

> [!note] Data crossing boundaries
> Clean architecture also says that data passed across a boundary should be in the form most convenient for the *inner* circle. Don't pass an ORM row or a Flask `Request` into a use case. In Martin's stated boundary rule, pass simple values or dedicated data-transfer structures, not entities or database rows. The repository example above illustrates ports and adapters; it does not implement every Clean Architecture boundary prescription.

## Key takeaways
- The composition root selects and connects concrete dependencies.
- Passing objects through constructors is dependency injection.
- Clean architecture permits source dependencies only inward and prescribes simple boundary data.
- Onion, clean and hexagonal architecture share inward dependency direction while describing boundaries differently.

## Further reading
- [The Clean Architecture — Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Onion Architecture — Jeffrey Palermo](https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/)
- [Cosmic Python: Dependency Injection](https://www.cosmicpython.com/book/chapter_13_dependency_injection.html)
