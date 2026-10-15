---
id: sep-solid-dependency-direction
title: Let policy define its dependencies
level: intermediate
minutes: 3
summary: Dependency inversion concerns the direction of source-code dependencies.
sourceLesson: sep-solid
---

SOLID examines responsibility, extension, subtyping, interfaces and dependency direction. This unit focuses on one of those questions; the earlier units establish the shared vocabulary.

## D: Dependency inversion principle

Two parts:

1. High-level modules should not depend on low-level modules. **Both should depend on abstractions.**
2. Abstractions should not depend on details. Details should depend on abstractions.

"High-level" means policy (business rules); "low-level" means mechanism (databases, HTTP, files).

```python
# Construction binds policy to vendors.
# Before: policy depends on detail
class InvoiceService:
    def __init__(self):
        self.db = PostgresClient(DSN)
        self.mail = SmtpMailer("smtp")

    def bill(self, cust):
        ...
```

`InvoiceService` constructs concrete clients, making isolated tests and substitutions harder; monkey-patching can still replace those names in Python. Injecting a narrow abstraction makes the seam explicit.

```python
# Pass implementations through this seam.
# After: policy owns the abstraction
class InvoiceRepo(Protocol):
    def save(self, inv): ...

class Mailer(Protocol):
    def send(self, to, body): ...

class InvoiceService:
    def __init__(self, repo: InvoiceRepo,
                 mail: Mailer):
        self.repo = repo
        self.mail = mail
```

```
 Before:
   InvoiceService --> PostgresClient

 After:
   InvoiceService --> InvoiceRepo
                          ^
                          | implements
   PostgresRepo ----------+
```

The arrow from the database now points *up* towards the abstraction: that's the inversion. Crucially, the interface belongs to the high-level module and is shaped by what it needs, not by what Postgres happens to offer.

### DIP is not the same as dependency injection

- **Dependency injection** is a technique: pass dependencies in (constructor, parameter) rather than creating them inside.
- **Dependency inversion** is a design principle about which way source-code dependencies point.

You can inject a concrete `PostgresClient` (DI without DIP), and you can follow DIP with a factory instead of injection. They work well together, and DI frameworks (Spring, Guice) are just one way to wire it up. Python projects usually manage with plain constructor arguments.

## Where SOLID goes wrong

- **Interface explosion.** An `IUserService` with exactly one implementation, created "for DIP", can add indirection without a demonstrated benefit. Introduce the abstraction when there's a second implementation or a real need to isolate (tests count).
- **SRP as "one method per class".** Splitting to the point where a feature is spread over twenty classes destroys cohesion. The test is actors and reasons to change, not size.
- **OCP everywhere.** Designing every class for extension is speculative; most code is best closed by simply being easy to edit.
- **Inheritance hierarchies.** Most LSP trouble starts with inheritance used just to share code. Prefer composition; inherit only when the subtype truly honours the contract.

## Key takeaways
- Dependency inversion concerns the direction of source-code dependencies.
- Dependency injection passes dependencies in and can still depend on a concrete detail.
- Introduce abstraction for a real boundary or substitution need, and keep related behaviour cohesive.

## Further reading
- [injection](https://martinfowler.com/articles/injection.html)
- [peps.python.org](https://peps.python.org/pep-0544/)
