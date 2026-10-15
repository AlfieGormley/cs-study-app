---
id: para-object-invariants
title: Objects, invariants and privacy
level: basic
minutes: 3
sourceLesson: para-oop
summary: Encapsulation protects an explicit object contract.
---

**Object-oriented programming (OOP)** organises a program around **objects**: bundles of state (fields) and the behaviour (methods) that operates on it. Instead of free-floating data passed to free-floating procedures, each piece of data comes with the operations allowed on it.

The ideas came from **Simula 67** (built for simulations, where "objects" were ships and customers) and **Smalltalk** (Alan Kay and colleagues at Xerox PARC in the 1970s). Kay has said the core idea was **messaging**: objects are like little computers that communicate only by sending each other messages. C++, Java, C#, Python and JavaScript all inherited some version of this.

OOP is often combined with imperative code, but objects may be immutable and their methods may be pure. What it adds is a way to structure that state. Four ideas carry most of the weight: encapsulation, inheritance, composition and polymorphism.

## Encapsulation

**Encapsulation** means an object hides its internal state and exposes only operations that keep that state valid. The rules that must always hold ("balance is never negative") are called invariants, and encapsulation is how you protect them.

```python
# Validate integer pence before mutation.
class Account:
    def __init__(self):
        self._balance = 0

    def deposit(self, amount):
        if type(amount) is not int:
            raise TypeError("integer pence")
        if amount <= 0:
            raise ValueError("must be > 0")
        self._balance += amount

    def withdraw(self, amount):
        if type(amount) is not int:
            raise TypeError("integer pence")
        if amount <= 0:
            raise ValueError("must be > 0")
        if amount > self._balance:
            raise ValueError("insufficient")
        self._balance -= amount

    @property
    def balance(self):
        return self._balance
```

This educational account uses integer pence and rejects nonpositive amounts. Callers respecting the public API use these methods, so validation is centralized. Python’s underscore convention does not prevent direct mutation of `_balance`; this is not a concurrent or production banking implementation.

How strictly languages enforce this varies:

| Language | Mechanism | Enforced? |
|---|---|---|
| Java, C# | `private`, `protected` | By compiler |
| Python | `_name` convention | No |
| Python | `__name` mangling | Weakly |
| JavaScript | `#field` | By runtime |

In Python, `self.__balance` inside class `Account` is renamed to `self._Account__balance`. That avoids accidental clashes in subclasses but is not real privacy. Python's culture is "we are all consenting adults".

## Key takeaways
- Encapsulation protects an explicit object contract.
- Python privacy conventions differ from enforced access controls.

## Further reading
- [Python: classes and private variables](https://docs.python.org/3.12/tutorial/classes.html)
- [Simula: the birth of object orientation](https://www.mn.uio.no/ifi/english/about/ole-johan-dahl/bibliography/the-birth-of-object-orientation-the-simula-languages.pdf)
