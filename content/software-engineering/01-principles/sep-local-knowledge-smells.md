---
id: sep-local-knowledge-smells
title: Keep knowledge beside the behaviour it protects
level: intermediate
minutes: 3
summary: The Law of Demeter limits knowledge of another object’s structure.
sourceLesson: sep-coupling-cohesion
---

Coupling concerns dependencies across a boundary; cohesion concerns the responsibilities grouped inside it. Use both when considering a design change.

## Two practical rules

### The Law of Demeter

"Only talk to your immediate friends." A method should call methods on itself, its parameters, objects it creates, and its direct fields, not on objects returned by those.

```python
# Changing any link can affect this caller.
# Train wreck: knows the whole chain
city = order.customer.address.city
```

The caller is now coupled to `Order`, `Customer` and `Address`. Restructure any of them and this line breaks.

```python
# The order hides its internal structure.
# Ask the nearest object
city = order.shipping_city()
```

Don't apply it mechanically. Chaining on data structures and fluent builders (`query.filter(...).order_by(...)`) isn't a violation in spirit, because you are not reaching through other objects' internals.

### Tell, don't ask

Rather than extracting data from an object to make a decision about it, tell the object what you want and let it decide.

```python
# withdraw owns the balance invariant.
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

## Key takeaways
- The Law of Demeter limits knowledge of another object’s structure.
- Tell, don’t ask puts a decision near the data and invariant it protects.
- Shotgun surgery and divergent change suggest different boundary problems.

## Further reading
- [object formulation](https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/object-formulation.html)
- [TellDontAsk](https://martinfowler.com/bliki/TellDontAsk.html)
- [smells](https://refactoring.guru/refactoring/smells)
