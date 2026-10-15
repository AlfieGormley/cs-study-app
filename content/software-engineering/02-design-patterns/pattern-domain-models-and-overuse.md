---
id: pattern-domain-models-and-overuse
title: Domain models and unnecessary abstractions
level: advanced
minutes: 3
sourceLesson: pattern-anti-patterns
summary: Keep real invariants in a design that reliably enforces them.
---

## Anaemic domain model

Martin Fowler's term (2003) for domain objects that are just bags of getters and setters, with all the business rules living in separate "service" classes. You get the cost of an object model (mapping, classes) without the benefit (behaviour next to the data it protects), and invariants can be broken from anywhere.

This one is contested. In data-pipeline or CRUD-heavy code, plain data plus functions is often the clearest design, and functional programmers would argue it's the right default. It becomes a problem when there are real business rules that keep being re-implemented, or violated, outside the objects.

## Pattern overuse

The anti-pattern this module most needs to warn about: **using patterns because they exist**.

```python
class GreeterFactory:
    def create(self):
        return EnglishGreeter()

class EnglishGreeter:
    def greet(self, name):
        return f"Hello, {name}"

# No alternative product needs a factory.
g = GreeterFactory().create()
print(g.greet("Ada"))
```

That is two classes and a factory for what is really `f"Hello, {name}"`. Signs of patternitis:

- Interfaces with one implementation and no test double.
- Factories that only ever create one class.
- Layers that only forward calls.
- Class names built from pattern names (`AbstractStrategyFactoryProvider`).

The fix is to inline the indirection until a second real variant arrives.

## Key takeaways
- Keep real invariants in a design that reliably enforces them.
- Plain data and pure functions can be appropriate when there are few business rules.
- A pattern name does not justify an extra interface, factory or forwarding layer.

## Further reading
- [Anemic Domain Model — Martin Fowler](https://martinfowler.com/bliki/AnemicDomainModel.html)
- [Inversion of Control Containers and Dependency Injection — Martin Fowler](https://martinfowler.com/articles/injection.html)
