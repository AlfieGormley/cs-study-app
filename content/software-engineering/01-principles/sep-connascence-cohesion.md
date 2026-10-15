---
id: sep-connascence-cohesion
title: What must change together?
level: intermediate
minutes: 3
summary: Connascence names the agreement that must stay in step, including names, meanings and order.
sourceLesson: sep-coupling-cohesion
---

Coupling concerns dependencies across a boundary; cohesion concerns the responsibilities grouped inside it. Use both when considering a design change.

## Connascence: a finer vocabulary

**Connascence** ("born together") provides a more precise vocabulary for dependencies. Two pieces of code are connascent if changing one requires changing the other to keep the system correct.

Static forms, from weakest to strongest:

| Form | Both sides must agree on |
|---|---|
| Name | a name (`send_email`) |
| Type | a type |
| Meaning | what a value means (`3` = cancelled) |
| Position | argument or field order |
| Algorithm | the same algorithm (a hash) |

Dynamic forms concern agreements during execution and are generally stronger: **execution** order (call `open()` before `read()`), **timing**, **value** (two values must change together) and **identity** (both must reference the same object).

Consider **connascence strength**, **connascence locality** and **connascence degree** together. Locality describes how close the components are; degree counts how many share the agreement. Strong connascence inside one function is fine; the same between two services owned by different teams is a hazard. The rule of thumb is to **convert strong forms into weaker ones**, especially across boundaries:

```python
# Names remove dependence on argument order.
# Connascence of position
make_user("Ada", "Lovelace", 36, True)

# Weakened to connascence of name
make_user(first="Ada", last="Lovelace",
          age=36, admin=True)
```

```python
# Both checks still share the status rule.
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
# Separate methods use separate field sets.
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

## Key takeaways
- Connascence names the agreement that must stay in step, including names, meanings and order.
- Prefer weaker agreements across distant ownership boundaries.
- Non-overlapping field use is a clue that one class serves unrelated concerns.

## Further reading
- [connascence.io](https://connascence.io/)
- [Cohesion_(computer_science)](https://en.wikipedia.org/wiki/Cohesion_(computer_science))
