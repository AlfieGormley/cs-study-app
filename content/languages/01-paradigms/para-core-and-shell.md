---
id: para-core-and-shell
title: A functional core with an imperative shell
level: intermediate
minutes: 3
sourceLesson: para-multi-paradigm
summary: Supply external facts as parameters to pure decision functions.
---

A decision function is easier to test when the facts it needs arrive as arguments. Keep the work that obtains and stores those facts in an outer layer.

## Functional core, imperative shell

A common way to mix paradigms in one program is the pattern Gary Bernhardt called **functional core, imperative shell**. Put the decisions in pure functions. Keep the side effects (network, database, clock, files) in a thin outer layer that calls them.

```python
# Pass the clock value into the pure core.
# Core: pure, easy to test
def apply_discount(order, today):
    if today.weekday() == 4:   # Friday
        return order.total * 0.9
    return order.total

# Shell: effects, kept thin
def handle(order_id, db, clock):
    order = db.load(order_id)
    total = apply_discount(
        order, clock.today())
    db.save_total(order_id, total)
```

The core is tested with plain values and no mocks: pass in an order and a date, check the number. The shell still needs integration tests for failures, retries, transactions and other relevant boundary behavior. Notice that `today` is a *parameter*, not a call to `date.today()` inside the core. Hiding the clock call inside would make the function impure and its tests depend on the day you run them.

```
+---------------------------------+
| shell: HTTP, DB, clock, logging |
|   +-------------------------+   |
|   | core: pure decisions    |   |
|   | (values in, values out) |   |
|   +-------------------------+   |
+---------------------------------+
```

This scales up to architecture. Redux reducers and Elm's update function put a pure state-transition function at the centre. Event-sourced systems can use the same approach when replaying events; event sourcing itself specifies storing events, not a universal guarantee that every handler is pure.

## Key takeaways
- Supply external facts as parameters to pure decision functions.
- The effectful shell still needs integration tests and failure handling.

## Further reading
- [Functional Core, Imperative Shell](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)
- [Elm architecture](https://guide.elm-lang.org/architecture/)
