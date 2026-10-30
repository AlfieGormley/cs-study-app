---
id: sep-local-knowledge-smells
title: Keep knowledge beside the behaviour it protects
level: intermediate
minutes: 4
summary: The Law of Demeter limits knowledge of another object’s structure.
sourceLesson: sep-coupling-cohesion
---

Coupling often creeps in one line at a time, as code reaches into other objects to fetch what it needs. This lesson covers two rules of thumb for keeping that knowledge local, and the code smells that show when it has spread.

## Two practical rules

### The Law of Demeter

Ian Holland proposed this rule in 1987 on the Demeter project at Northeastern University: "only talk to your immediate friends." A method should call methods on itself, its parameters, objects it creates, and its direct fields, not on objects returned by those.

```python
# Train wreck: knows the whole chain
city = order.customer.address.city
```

The caller is now coupled to `Order`, `Customer` and `Address`. Restructure any of them and this line breaks.

```python
# Ask the nearest object
city = order.shipping_city()
```

Don't apply it mechanically. Chaining on data structures and fluent builders (`query.filter(...).order_by(...)`) isn't a violation in spirit, because you are not reaching through other objects' internals. Applied rigidly, the law can also force many small forwarding methods onto a class, which widens its interface.

> [!analogy] Real-world analogy: the paperboy and the wallet
> David Bock's well-known illustration: a paperboy collecting payment does not take the customer's wallet, open it and remove the money. He asks the customer to pay, and the customer decides whether the money comes from a wallet, a jar or a card.
>
> **How it maps:** `customer.wallet.take(amount)` is the train wreck: the caller depends on the customer *and* the wallet. `customer.pay(amount)` talks only to an immediate friend and leaves the customer's internals free to change. Letting the customer, who owns the money, decide is also tell, don't ask.
>
> **Where it stops:** People can refuse or negotiate; a method call simply runs. The picture also hides the law's cost: adding a forwarding method for every need can bloat a class, so apply it where hiding structure protects a likely change.

### Tell, don't ask

This rule is most often associated with Andy Hunt and Dave Thomas. Rather than extracting data from an object to make a decision about it, tell the object what you want and let it decide.

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

It is a heuristic, not a law. Martin Fowler writes that he does not use it himself: pushed too far it turns into removing every getter, and sometimes objects collaborate well simply by providing information. Reporting and display code, for instance, legitimately asks objects for data.

## Smells that point at coupling problems

These names come from the code-smell catalogue in Fowler and Beck's *Refactoring*.

- **Shotgun surgery**: one change requires small edits in many modules. Something that should be in one place is spread out.
- **Divergent change**: one module changes for many unrelated reasons. It has low cohesion.
- **Feature envy**: a method uses another object's data more than its own. It probably belongs over there.
- **Inappropriate intimacy**: two classes access each other's private parts.

## Key takeaways
- The Law of Demeter limits knowledge of another object’s structure.
- Tell, don’t ask puts a decision near the data and invariant it protects.
- Shotgun surgery and divergent change suggest different boundary problems.

## Further reading
- [Law of Demeter: object formulation (Northeastern)](https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/object-formulation.html)
- [Bock: The Paperboy, the Wallet, and the Law of Demeter](https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/paper-boy/demeter.pdf)
- [Martin Fowler: Tell Don't Ask](https://martinfowler.com/bliki/TellDontAsk.html)
- [Refactoring.Guru: code smells](https://refactoring.guru/refactoring/smells)
