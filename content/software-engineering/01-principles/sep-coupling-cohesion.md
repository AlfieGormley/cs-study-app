---
id: sep-coupling-cohesion
title: Coupling and cohesion
level: intermediate
minutes: 11
summary: The two forces behind almost every design decision, the classic scales for measuring them, connascence, the Law of Demeter and how to spot trouble in real code.
---

Ask why a "small" change took three days and touched eleven files, and one possible cause is the code was **tightly coupled** and **poorly cohesive**. These two ideas, introduced by Larry Constantine and colleagues in the 1970s *structured design* work, still underpin most design advice, including SOLID and microservice boundaries.

- **Coupling** is how much one module depends on another. Low coupling reduces how often a change in one requires changing the other.
- **Cohesion** is how closely the things *inside* a module belong together. High cohesion means a module has one clear purpose.

The goal is **low coupling, high cohesion**. They pull in the same direction: if related things live together, fewer connections have to cross module boundaries.

```
 Poor                    Good
 +-----+  +-----+        +-----+  +-----+
 | a c |==| b d |        | a b |--| c d |
 | e   |==| f   |        | e f |  |     |
 +-----+  +-----+        +-----+  +-----+
 many links across       related things
 the boundary            together, one link
```

## Coupling: what it really means

Every dependency is a reason a change in one place might force a change elsewhere. The question is not "is there a dependency?" (there always is) but "how much does each side need to know about the other?"

### The classic coupling scale

A traditional ordering from tighter to looser coupling follows. It is a design heuristic, not a universal ranking of harm:

| Type | One module... |
|---|---|
| Content | reaches into another's internals |
| Common | shares global mutable data |
| External | shares a format or device |
| Control | passes a mode flag steering the other |
| Stamp | passes a whole record, uses a bit |
| Data | passes only the values needed |

Some Python examples:

```python
# Content: poking a private field
order._items.append(item)

# Common: shared mutable global
CONFIG["currency"] = "EUR"

# Control: caller steers internal logic
report(data, mode="summary")

# Stamp: whole object, uses one field
def greet(user):
    return f"Hi {user.name}"

# Data: just what it needs
def greet(name):
    return f"Hi {name}"
```

Stamp coupling isn't always bad: passing `user` lets the function evolve without changing its signature. The dependency here is on an object exposing `name`. In dynamically typed Python it need not be a complete `User`; a small test double with that attribute works.

### Coupling you can't see

The most dangerous coupling is **implicit**: two modules agree on something that isn't written in either's interface.

- Both assume dates are in UTC.
- A consumer relies on a list being sorted, though the producer never promised it.
- Two services both know that status `3` means "cancelled".

Change one side and the other breaks with no compile error and often no test failure.

## Connascence: a finer vocabulary

Meilir Page-Jones introduced **connascence** ("born together") in the 1990s as a more precise language. Two pieces of code are connascent if changing one requires changing the other to keep the system correct.

Static forms, from weakest to strongest:

| Form | Both sides must agree on |
|---|---|
| Name | a name (`send_email`) |
| Type | a type |
| Meaning | what a value means (`3` = cancelled) |
| Position | argument or field order |
| Algorithm | the same algorithm (a hash) |

Dynamic forms (visible only at runtime) are stronger still: **execution** order (call `open()` before `read()`), **timing**, **value** (two values must change together) and **identity** (both must reference the same object).

Connascence also has **locality** and **degree**. Strong connascence inside one function is fine; the same between two services owned by different teams is a hazard. The rule of thumb is to **convert strong forms into weaker ones**, especially across boundaries:

```python
# Connascence of position
make_user("Ada", "Lovelace", 36, True)

# Weakened to connascence of name
make_user(first="Ada", last="Lovelace",
          age=36, admin=True)
```

```python
# Connascence of meaning
if order.status == 3: ...

# Weakened to connascence of name
if order.status == Status.CANCELLED: ...
```

## Cohesion: does this belong together?

The classic cohesion scale, from worst to best:

| Type | Grouped because... |
|---|---|
| Coincidental | no reason (`utils.py`) |
| Logical | same category, different jobs |
| Temporal | they run at the same time |
| Procedural | they run in sequence |
| Communicational | they use the same data |
| Sequential | output of one feeds the next |
| Functional | together they do one task |

A `utils.py` holding `slugify`, `retry` and `parse_vat_number` is coincidentally cohesive. Importers can become coupled to unrelated module-level imports and initialisation; ownership may also become unclear. A `startup()` function that opens the database, warms caches and sends a metric is temporally cohesive: change any one of those and you edit a function about all of them.

### Spotting low cohesion in a class

A useful code smell to look for: **do methods use non-overlapping sets of fields?**

```python
class Customer:
    def __init__(self):
        self.name = ...
        self.email = ...
        self.card_number = ...
        self.card_expiry = ...

    def send_newsletter(self):
        ...  # uses name, email

    def charge(self, amount):
        ...  # uses card_number, card_expiry
```

This suggests two concerns: contact details and a payment method. Metrics like LCOM (lack of cohesion of methods) formalise exactly this.

## Two practical rules

### The Law of Demeter

"Only talk to your immediate friends." A method should call methods on itself, its parameters, objects it creates, and its direct fields, not on objects returned by those.

```python
# Train wreck: knows the whole chain
city = order.customer.address.city
```

The caller is now coupled to `Order`, `Customer` and `Address`. Restructure any of them and this line breaks.

```python
# Ask the nearest object
city = order.shipping_city()
```

Don't apply it mechanically. Chaining on data structures and fluent builders (`query.filter(...).order_by(...)`) isn't a violation in spirit, because you are not reaching through other objects' internals.

### Tell, don't ask

Rather than extracting data from an object to make a decision about it, tell the object what you want and let it decide.

```python
# Ask: logic lives outside the data
if acct.balance >= amount:
    acct.balance -= amount
else:
    raise InsufficientFunds()

# Tell: logic lives with the data
acct.withdraw(amount)
```

This raises cohesion (the rule lives with the balance it protects) and lowers coupling (callers no longer know how withdrawals work).

## Smells that point at coupling problems

- **Shotgun surgery**: one change requires small edits in many modules. Something that should be in one place is spread out.
- **Divergent change**: one module changes for many unrelated reasons. It has low cohesion.
- **Feature envy**: a method uses another object's data more than its own. It probably belongs over there.
- **Inappropriate intimacy**: two classes access each other's private parts.

## Measuring it

A module-level variant of Robert C. Martin's package metrics gives a rough number. Here we count distinct modules (other formulations count classes across package boundaries). Start with two counts for a module:

- **Afferent coupling**: how many other modules depend on it (incoming dependencies). "Afferent" means "carried towards".
- **Efferent coupling**: how many other modules it depends on (outgoing dependencies). "Efferent" means "carried away".

**Instability** combines them into one number: the share of a module's dependency links that point outwards. Use it to ask "if I change this module, how many others might break?" and "how exposed is it to changes elsewhere?"

```formula
I = Ce / (Ca + Ce)
where
I: the module's instability, a plain ratio with no unit, from 0 (maximally stable) to 1 (maximally unstable)
Ce: efferent coupling, the number of other modules this module depends on (outgoing)
Ca: afferent coupling, the number of other modules that depend on this module (incoming)
In words: instability is outgoing dependencies divided by all dependencies, in either direction. The more a module leans on others, and the fewer lean on it, the closer it is to 1.
```

A worked example. A `money` module is imported by 9 other modules and imports only 1 itself. An `admin_report` module is imported by nothing and imports 4 modules:

```formula
I_money = 1 / (9 + 1) = 0.1
I_report = 4 / (0 + 4) = 1
where
I_money: the instability of the money module, a ratio with no unit
I_report: the instability of the admin_report module, a ratio with no unit
In words: money has 9 incoming and 1 outgoing link, so it is very stable (0.1); admin_report has only outgoing links, so it is maximally unstable (1).
```

A module that many others use and that depends on little (I near 0, like `money`) is hard to change safely, so it should be abstract and slow-moving. A value near 1 means outgoing dependencies dominate, not that nobody depends on it. Exactly I = 1 means Ca = 0 and Ce > 0, as with `admin_report`.

Limits of the metric:

- It needs Ca + Ce to be positive. An isolated module (no links either way) divides 0 by 0, so its instability is undefined unless a tool specifies a convention.
- Every dependency counts as 1, whether it uses one function or fifty.
- The ratio measures structural dependence, not observed change frequency.

The **stable dependencies principle** says dependencies should point towards stability: a module should depend only on modules whose instability is lower than its own.

## Trade-offs

- **Decoupling has a price.** Every interface, event bus or message queue added to cut a dependency is something to understand and debug. An event fired into the void is loosely coupled and very hard to trace.
- **Coupling to stable things is cheap.** Depending on documented Python standard-library APIs is coupling to compatibility commitments; releases can still deprecate or remove APIs.
- **Distributed coupling is the worst kind.** Two microservices that must deploy together are tightly coupled *and* separated by a network. That is the "distributed monolith".
- **Cohesion is contextual.** Grouping by technical layer (`models/`, `views/`) is logical cohesion; grouping by feature (`billing/`, `search/`) is usually more functional. Neither is wrong everywhere.

## Key takeaways
- Coupling measures how much modules depend on each other; cohesion measures how well a module's contents belong together. Aim for low coupling and high cohesion.
- Coupling ranges from content and common (worst) to data (best); cohesion ranges from coincidental (worst) to functional (best).
- Connascence names *what* two pieces of code must agree on; weaken strong forms (position, meaning) to weaker ones (name), especially across boundaries.
- The Law of Demeter and "tell, don't ask" keep knowledge local.
- Shotgun surgery and divergent change are the symptoms; instability (outgoing dependencies as a share of all dependencies) is one rough metric.
- Decoupling is not free; invest where change is likely and boundaries are costly.

## Further reading
- [Coupling (computer programming) — Wikipedia](https://en.wikipedia.org/wiki/Coupling_(computer_programming))
- [Cohesion (computer science) — Wikipedia](https://en.wikipedia.org/wiki/Cohesion_(computer_science))
- [Connascence.io](https://connascence.io/)
- [Reducing Coupling — Martin Fowler (IEEE Software, PDF)](https://martinfowler.com/ieeeSoftware/coupling.pdf)
- [Tell Don't Ask — Martin Fowler](https://martinfowler.com/bliki/TellDontAsk.html)
- [Law of Demeter — Wikipedia](https://en.wikipedia.org/wiki/Law_of_Demeter)
- [Software package metrics — Wikipedia](https://en.wikipedia.org/wiki/Software_package_metrics)
