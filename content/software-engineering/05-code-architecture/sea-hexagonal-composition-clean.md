---
id: sea-hexagonal-composition-clean
sourceLesson: sea-hexagonal
title: Composition roots and clean architecture
level: intermediate
minutes: 4
summary: Wire concrete adapters at the entry point and compare hexagonal, onion and clean boundaries.
---

The Python core from the previous unit can run with real adapters or with fakes. Something at the outer edge has to choose which. This unit shows where that choice lives, then compares hexagonal architecture with two close relatives.

## The composition root

The place that chooses which adapters to plug in is the **composition root**, usually at the entry point (`main.py`, the app factory, or a `bootstrap.py`). In a large application the wiring may be split across a few factory functions, but it still happens at the outer edge, never inside the core.

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

No dependency-injection framework is needed. Passing objects to constructors, as here, *is* dependency injection; frameworks only automate the wiring when it grows large.

## Clean and onion architecture

Two later variants describe the same idea with concentric circles.

- **Onion architecture** (Jeffrey Palermo, 2008): domain model in the centre, then domain services, then application services, with UI, infrastructure and tests in the outer ring.
- **Clean architecture** (Robert C. Martin, a 2012 blog post, developed further in his 2017 book *Clean Architecture*): entities in the centre, then use cases, then interface adapters (controllers, presenters, gateways), then frameworks and drivers. Martin says the four circles are schematic and you may need more; only the dependency rule below is fixed.

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

The differences are largely vocabulary and emphasis. All three keep business logic independent of frameworks, UI and storage, and all three get there by inverting dependencies at the boundary. How much of the extra structure to adopt (separate presenters, request and response objects for every use case) is debated among practitioners; the next unit weighs those costs.

> [!note] Data crossing boundaries
> Martin also says that data crossing a boundary should always be in the form most convenient for the *inner* circle: simple values or small data-transfer structures, not entities or database rows. So a Flask `Request` or an ORM row never goes into a use case. The repository in the previous unit hands domain `Order` objects across its port, as is normal in ports and adapters; it doesn't try to follow every Clean Architecture prescription.

## Key takeaways
- The composition root selects and connects concrete dependencies.
- Passing objects through constructors is dependency injection.
- Clean architecture permits source dependencies only inward and prescribes simple data at boundaries; how much of its structure to adopt is debated.
- Onion, clean and hexagonal architecture share inward dependency direction while describing boundaries differently.

## Further reading
- [The Clean Architecture — Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Onion Architecture — Jeffrey Palermo](https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/)
- [Cosmic Python: Dependency Injection](https://www.cosmicpython.com/book/chapter_13_dependency_injection.html)
