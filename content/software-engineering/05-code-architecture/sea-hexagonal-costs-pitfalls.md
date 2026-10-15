---
id: sea-hexagonal-costs-pitfalls
sourceLesson: sea-hexagonal
title: Adapter costs and leaky boundaries
level: intermediate
minutes: 4
summary: Judge when adapters pay for themselves and detect technology or business policy leaking across ports.
---

With ports, adapters and wiring in place, the remaining question is whether the boundary protects enough business behavior to justify its cost.

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
- Ports protect a meaningful core at the cost of mapping and indirection.
- Replacement adapters must preserve port semantics, not just method names.
- Ports belong at external boundaries; pure domain values need no port between each other.
- Thin CRUD tools may be better served by framework defaults.
- Keep technology out of ports and business policy out of adapters.

## Further reading
- [Hexagonal Architecture — Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Architecture Patterns with Python: Repository Pattern](https://www.cosmicpython.com/book/chapter_02_repository.html)
- [Netflix: Ready for Changes with Hexagonal Architecture](https://netflixtechblog.com/ready-for-changes-with-hexagonal-architecture-b315ec967749)
