---
id: sea-ddd-language-values
sourceLesson: sea-ddd
title: Domain language, entities and values
level: intermediate
minutes: 5
summary: Use shared business vocabulary and distinguish persistent identity from immutable values.
---

Most hard software isn't hard because of the technology. It's hard because the *business* is complicated: insurance underwriting, freight scheduling, clinical trials. Eric Evans' 2003 book *Domain-Driven Design* argues that in such systems the most valuable design work is modelling the domain itself, in close collaboration with the people who understand it.

DDD has two halves:

- **Strategic design**: how to carve a large domain into parts (bounded contexts) and how those parts relate.
- **Tactical design**: building blocks for the model inside one part: entities, value objects, aggregates, domain events, repositories.

Teams often adopt the tactical patterns and skip the strategic ones. Classes named `Entity` and `Repository` don't make a useful domain model on their own; the insight comes from the boundaries and the language.

## Ubiquitous language

The starting point is a shared vocabulary between developers and domain experts, used in conversation, documents *and code*. If the underwriters say "a policy is **bound**", the code says `policy.bind()`, not `policy.set_status(3)`.

When the code uses different words from the business, every conversation needs translation, and translation is where misunderstandings breed. A mismatch you can't resolve is often a sign that you're straddling two contexts (see below).

## Entities: identity that persists

An **entity** is defined by its identity, not its attributes. A customer who changes their name and address is still the same customer. Two customers with identical names are different people.

```python
class Customer:
    def __init__(self, customer_id, name):
        self.id = customer_id
        self.name = name

    def __eq__(self, other):
        # Identity survives attribute
        # changes.
        return (isinstance(other, Customer)
                and other.id == self.id)

    # Mutable entities are unhashable here.
    __hash__ = None
```

An entity has a lifecycle (created, changed, perhaps archived), and its identifier must stay the same throughout. In Python, a class that defines `__eq__` without `__hash__` is already unhashable; the `__hash__ = None` line just says so openly. That's a cautious choice: these objects can't go in a set or be dict keys. A common alternative is to hash on the id alone, which is safe as long as the id never changes.

## Value objects: defined by their values

A **value object** has no identity. Two equal Money values represent the same amount and currency, and either will do. Value objects should be **immutable**: to "change" one you make a new one.

Whether something is an entity or a value depends on the model, not the thing. In a shop, any £10 is as good as another. A central bank that tracks individual banknotes by serial number would model each note as an entity.

> [!analogy] Real-world analogy: a passport and a £10 note
> If someone borrows £10 and pays you back with a different note, you don't mind. A passport office is different: it cares which person a passport belongs to, not what they currently look like. When you renew with a new photo, or after changing your name, its records still refer to the same person.
>
> **How it maps:** The £10 is a value object: equal amount means interchangeable. The person the passport office tracks is an entity, identified by something stable rather than by their current details; a new photo or name is an attribute change, not a new person.
>
> **Where it stops:** A real note has a serial number, so a different model could track it as an entity. And the passport office checks identity with documents and interviews; in code, identity is just an id field, so nothing stops two records being created for the same real person unless your system prevents it.

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    # Reject invalid values at construction.
    def __post_init__(self):
        if not isinstance(
                self.amount, Decimal):
            raise TypeError("Decimal only")
        if not self.amount.is_finite():
            raise ValueError("nonfinite")
        if self.amount < 0:
            raise ValueError("negative")
        allowed = {"GBP", "USD"}
        if self.currency not in allowed:
            raise ValueError("currency")

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency != self.currency:
            raise ValueError("currency")
        # Return a new same-currency value.
        total = self.amount + other.amount
        return Money(total, self.currency)
```

By default a dataclass compares objects field by field, so `Money(Decimal("5"), "GBP") == Money(Decimal("5"), "GBP")` is `True`. Adding `frozen=True` blocks ordinary attribute assignment and, together with that equality, makes the dataclass generate a hash, so values can go in sets and dict keys. Two limits: frozen is shallow (a list inside could still be changed), and hashing fails if any field is itself unhashable.

This `Money` deliberately accepts only non-negative GBP or USD amounts. Other domains need negative amounts (refunds, balances) and their own currency and rounding rules.

Why bother? Value objects:

- **Validate once**: this example checks construction and same-currency addition. Currency conversion, rounding, context precision and business-specific limits still need explicit policies.
- **Remove primitive obsession**: `Email`, `Postcode` and `Quantity` say more than `str` and `int`.
- **Are safe to share**: immutable objects can't be changed behind your back.

> [!tip] Default to value objects
> Most concepts in a model are values: date ranges, addresses, amounts, coordinates. Make something an entity only when you genuinely need to track it as "the same thing" over time.

## Key takeaways
- DDD models a complex business with its domain experts.
- Ubiquitous language connects conversations, documents and code within a context.
- Entities retain identity as attributes change; value objects compare by their values.
- Frozen dataclasses are not deeply immutable, and generated hashing needs hashable fields.

## Further reading
- [Domain-Driven Design Reference — Eric Evans](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf)
- [Value Object — Martin Fowler](https://martinfowler.com/bliki/ValueObject.html)
- [dataclasses — Python documentation](https://docs.python.org/3/library/dataclasses.html)
