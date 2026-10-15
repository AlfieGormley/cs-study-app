---
id: pattern-values-and-dependencies
title: Explicit values and visible dependencies
level: advanced
minutes: 3
sourceLesson: pattern-anti-patterns
summary: Named constants and domain value objects make units and rules visible.
---

## Magic numbers and primitive obsession

```python
# Units and state meaning are concealed.
if user.status == 3 and amount > 9999:
    fee = amount * 0.029 + 20
```

What's status 3? Why 9999? Is 20 pence or pounds? **Magic numbers** hide meaning; named constants or enums restore it.

**Primitive obsession** is the wider smell: representing domain concepts as raw strings, ints and floats. Money as a float invites rounding errors (`0.1 + 0.2 != 0.3`); an email as a `str` means validation is repeated, or forgotten, everywhere. A small type (`Money` built on `Decimal`, an `Email` value object) puts the rules in one place.

## Singleton abuse and service locator

The earlier short lesson on shared instances covered the risks of hidden global state. The anti-pattern is using them as a way to avoid passing dependencies around: `Config.instance()`, `Db.instance()` and `Cache.instance()` reached for from anywhere.

**Service locator** is its more sophisticated cousin: a global registry you ask for dependencies (`locator.get(PaymentGateway)`). It's flexible, but dependencies obtained this way are hidden inside method bodies. Mark Seemann famously argued that it's an anti-pattern for this reason. The alternative is **dependency injection**: pass dependencies in through the constructor, so they're visible and replaceable.

## Key takeaways
- Named constants and domain value objects make units and rules visible.
- Decimal avoids binary representation error for base-ten inputs supplied as strings, subject to its arithmetic context.
- Constructor injection exposes dependencies that a service locator hides inside method bodies.

## Further reading
- [decimal — Python documentation](https://docs.python.org/3/library/decimal.html)
- [Floating-point arithmetic — Python documentation](https://docs.python.org/3/tutorial/floatingpoint.html)
- [Inversion of Control Containers and Dependency Injection — Martin Fowler](https://martinfowler.com/articles/injection.html)
