---
id: sep-solid-dependency-direction
title: Let policy define its dependencies
level: intermediate
minutes: 4
summary: Dependency inversion concerns the direction of source-code dependencies.
sourceLesson: sep-solid
---

Business rules tend to be the most valuable and longest-lived code, while databases, mail providers and frameworks come and go. This lesson is about which way the source-code dependencies between them should point.

## D: Dependency inversion principle

Robert C. Martin described this idea in his mid-1990s writing and set it out as a named principle in his 1996 article *The Dependency Inversion Principle*. It has two parts:

1. High-level modules should not depend on low-level modules. **Both should depend on abstractions.**
2. Abstractions should not depend on details. Details should depend on abstractions.

"High-level" means policy (business rules); "low-level" means mechanism (databases, HTTP, files).

```python
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

> [!analogy] Real-world analogy: a job description
> A bakery writes a job description: "can open the shop at 6 a.m. and run the till". Anyone who meets it can be hired, and the bakery's routine doesn't change when a new person starts.
>
> **How it maps:** The bakery is the high-level policy, and it writes the abstraction in terms of what it needs (`Mailer.send`), not in terms of one applicant's CV (a vendor's API). Each applicant is a low-level detail that must meet the description, so the dependency points from the detail to the abstraction. Whoever hires and introduces the new starter is doing dependency injection.
>
> **Where it stops:** People bring skills beyond the description and can negotiate it; an implementation simply has to match the interface. And a shop with one long-standing employee may not need a formal description, just as one concrete dependency doesn't always need an interface.

### DIP is not the same as dependency injection

- **Dependency injection** is a technique: pass dependencies in (constructor, parameter) rather than creating them inside.
- **Dependency inversion** is a design principle about which way source-code dependencies point.

You can inject a concrete `PostgresClient` (DI without DIP), and you can follow DIP with a factory instead of injection. They work well together, and DI frameworks (Spring, Guice) are just one way to wire it up. Python projects usually manage with plain constructor arguments.

## Where SOLID goes wrong

- **Interface explosion.** An `IUserService` with exactly one implementation, created "for DIP", can add indirection without a demonstrated benefit. Introduce the abstraction when there's a second implementation or a real need to isolate (tests count).
- **SRP as "one method per class".** Splitting to the point where a feature is spread over twenty classes destroys cohesion. The test is actors and reasons to change, not size.
- **OCP everywhere.** Designing every class for extension is speculative; most code is best closed by simply being easy to edit.
- **Inheritance hierarchies.** Much LSP trouble starts with inheritance used just to share code. Prefer composition; inherit only when the subtype truly honours the contract.

## Key takeaways
- Dependency inversion concerns the direction of source-code dependencies.
- Dependency injection passes dependencies in and can still depend on a concrete detail.
- Introduce abstraction for a real boundary or substitution need, and keep related behaviour cohesive.

## Further reading
- [Martin Fowler: Inversion of Control Containers and the Dependency Injection pattern](https://martinfowler.com/articles/injection.html)
- [Dependency inversion principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
- [PEP 544: Protocols](https://peps.python.org/pep-0544/)
