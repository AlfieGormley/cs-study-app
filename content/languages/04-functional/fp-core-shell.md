---
id: fp-core-shell
title: Passing effects into a functional core
level: basic
minutes: 3
sourceLesson: fp-pure-functions
summary: Keep external reads and writes in a thin shell.
---

Keep external reads and writes in a thin shell. This unit develops that mechanism using the earlier units as prerequisites.

## Functional core, imperative shell

Real programs must do I/O. The standard pattern, popularised by Gary Bernhardt, is a **functional core** wrapped in an **imperative shell**:

```
+------------------------------------+
| shell: read request, query DB,     |
|        call APIs, write response   |
|   +----------------------------+   |
|   | core: pure functions that  |   |
|   | decide what to do, given   |   |
|   | plain data                 |   |
|   +----------------------------+   |
+------------------------------------+
```

```python
# The shell supplies the external date.
# Core: pure, trivially testable
def apply_discount(order, today):
    if today.weekday() == 4:  # Friday
        t = order["total"] * 0.9
        return {**order, "total": t}
    return order

# Shell: impure, kept thin
def handle(order_id):
    order = db.load(order_id)
    today = date.today()
    new = apply_discount(order, today)
    db.save(new)
```

Notice the trick: instead of calling `date.today()` inside the core, the shell passes the date in. The impurity has been turned into a parameter. Tests can pass any date they like.

## Key takeaways
- Keep external reads and writes in a thin shell.
- Pass time and other external facts as inputs to decision functions.

## Further reading
- [Pio](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)
- [Python Fp](https://docs.python.org/3/howto/functional.html)
