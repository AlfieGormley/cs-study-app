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

Teams often adopt the tactical patterns and skip the strategic ones. Strategic boundaries deserve explicit attention; using entity and repository classes alone does not establish a useful domain model.

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

Keep the identifier of an entity stable throughout their lifecycle. The example leaves entities unhashable so mutable attributes cannot corrupt set/dict membership. Entities can have a lifecycle: created, changed, perhaps archived.

## Value objects: defined by their values

A **value object** has no identity. Two equal Money values represent the same amount and currency. Physical notes can have distinct serial-number identities in a different model. Value objects should be **immutable**: to "change" one you make a new one.

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

With the default `eq=True`, dataclass generates field equality; combining it with `frozen=True` normally generates a hash. Frozen blocks ordinary attribute assignment but does not deeply freeze contained objects, and hashing requires hashable fields. This example deliberately supports only nonnegative GBP/USD amounts; other domains may need negative money values and different currency/rounding rules. So `Money(Decimal("5"), "GBP") == Money(Decimal("5"), "GBP")` is `True`.

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
