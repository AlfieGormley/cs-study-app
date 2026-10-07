---
id: sepr-refactoring
title: Refactoring techniques
level: basic
minutes: 11
summary: What refactoring really is, the safety net it needs, the core moves from Fowler's catalogue, and how to restructure large systems with parallel change, branch by abstraction and the strangler fig.
---

**Refactoring** is changing the structure of code without changing what it does. Martin Fowler's definition has two parts: a refactoring is a small change that makes code easier to understand and cheaper to modify, *without changing its observable behaviour*; and *refactoring* (the activity) is applying a series of those small changes.

The key word is *behaviour-preserving*. If you rename a function and fix a bug in the same commit, you have done two things, and when something breaks you will not know which one caused it. Kent Beck's image is the **two hats**: when you add a feature you wear one hat, when you refactor you wear the other, and you swap often but never wear both at once.

## Why bother?

Code is read far more than it is written. Every feature you add lands in the shape the code already has. If that shape is awkward, the feature is slow to add and easy to get wrong.

Beck's advice sums up the workflow: "make the change easy (warning: this may be hard), then make the easy change." Refactoring is the first half. You reshape the code so the new feature fits naturally, then add it.

There are a few common moments to refactor:

- **Preparatory**: just before a feature, to make room for it.
- **Comprehension**: while reading confusing code, rename and extract until it makes sense, so the next reader gets your understanding for free.
- **Litter-pickup**: small improvements as you pass through (the "boy scout rule": leave the code a bit better than you found it).
- **Planned**: a dedicated chunk of work when neglect has made an area painful. Healthy teams need this less, because the other three keep it in check.

## The safety net: tests

You cannot claim behaviour is unchanged unless something checks it. Before refactoring, you need tests that cover the code you are about to touch, and they should be fast enough to run after every small step.

If the code has no tests, write **characterisation tests** first (Michael Feathers' term from *Working Effectively with Legacy Code*). You do not assert what the code *should* do; you record what it *currently* does, bugs included.

```python
def price(qty, item):
    total = qty * item
    if qty >= 500:
        return total - 100
    return total

def test_price_characterisation():
    # Whatever it returns today is "right"
    # for the purposes of refactoring.
    assert price(qty=0, item=10) == 0
    assert price(qty=3, item=10) == 30
    assert price(qty=600, item=10) == 5900
```

If a refactoring changes one of these outputs, you have changed behaviour, deliberately or not. Fix bugs afterwards, as a separate, visible change.

> [!tip] Commit at every green
> Make one small move, run the tests, commit. If the next step goes wrong you can discard the intended tracked-file edits with `git restore <paths>` after checking the diff (unrelated uncommitted work must be preserved) instead of debugging a half-finished restructure.

## Code smells: when to refactor

A **code smell** is a surface symptom that often (not always) signals a deeper design problem. Some common ones from Fowler's catalogue:

| Smell | Typical fix |
|---|---|
| Long function | Extract Function |
| Duplicated code | Extract, then reuse |
| Feature envy | Move Function |
| Data clumps | Introduce Parameter Object |
| Primitive obsession | Replace Primitive with Object |
| Shotgun surgery | Move related code together |
| Divergent change | Split the module |

Two of these are worth telling apart. **Shotgun surgery** is when one change forces edits in many places. **Divergent change** is the opposite: one module changes for many unrelated reasons. Both are coupling and cohesion problems seen from different directions.

## The core moves

Most day-to-day refactoring uses a handful of moves. Here is a messy function:

```python
def invoice(order):
    total = 0
    for line in order["lines"]:
        total += line["qty"] * line["price"]
    if order["country"] == "GB":
        total = total * 1.2
    print(f"Total: {total:.2f}")
```

**Extract Function** pulls a coherent piece into a named function. The name documents intent:

```python
def subtotal(lines):
    total = 0
    for line in lines:
        total += line["qty"] * line["price"]
    return total

def with_example_charge(amount, country):
    if country == "GB":
        return amount * 1.2
    return amount

def invoice(order):
    net = subtotal(order["lines"])
    gross = with_example_charge(
        net, order["country"])
    print(f"Total: {gross:.2f}")
```

For the supported numeric inputs, the arithmetic and printed output are preserved. This is a fictional country-tagged surcharge, not a VAT implementation or tax guidance. Keep the original accumulation loop: replacing it with `sum` can change floating-point results on Python 3.12 and later. Now each part can be tested and reused, and adding a new country's rate touches one small function.

Other moves you will use constantly:

- **Rename** (variable, function, class). The cheapest, most valuable refactoring. If you have to read a function's body to know what it does, its name is wrong.
- **Inline Function / Inline Variable**: the reverse of extract, when the indirection no longer earns its keep.
- **Extract Variable**: give a complicated expression a name.
- **Move Function**: put a function next to the data it uses most (the fix for feature envy).
- **Introduce Parameter Object**: `(start, end)` passed everywhere becomes a `DateRange`.
- **Replace Conditional with Polymorphism**: a `match` on type repeated in several places becomes one class per case.
- **Separate Query from Modifier**: a function that both returns a value and changes state is split, so reading never surprises you.

Modern IDEs (IntelliJ, PyCharm, VS Code with a language server) automate rename, extract and move. Automated refactorings are much safer than hand edits because the tool can resolve many references consistently, though dynamic code like `getattr(obj, name)` can still escape it.

## Refactoring code you do not fully control

Renaming a function is easy when you can update every caller in one commit. It is hard when callers live in other services, other teams or other companies.

### Parallel change (expand and contract)

Change an interface in three phases, each safe to deploy on its own:

```
1. Expand    add new_name(); old_name()
             calls it. Both work.
2. Migrate   move callers to new_name()
             one at a time.
3. Contract  delete old_name() once
             nothing calls it.
```

For columns, expand the schema and deploy atomic dual writes while still reading the old column. Drain every old-only writer, including jobs, before a race-safe backfill from the current row values; alternatively use database synchronization that also covers old writers. Validate equality before switching reads. Keep dual writes through the rollback window, then retire all old readers/writers before dropping the old column. Locks, transactions and conditional updates must prevent stale backfill data from overwriting newer values.

### Branch by abstraction

To replace a large internal component (say, an ORM or a payment library) without a long-lived branch:

1. Put an **abstraction layer** (an interface) in front of the old component.
2. Move all callers to use the abstraction.
3. Build the new implementation behind the same abstraction, switched by a flag.
4. Flip callers over gradually, then delete the old implementation and, if it no longer helps, the abstraction.

Everything is merged to the main branch continuously. The code always builds and ships.

### Strangler fig

For a whole legacy system, Fowler's **strangler fig** pattern (named after a vine that grows round a tree until it replaces it) routes traffic through a facade. New functionality goes into the new system; old routes are moved across one at a time until the legacy system handles nothing and can be switched off.

```
client -> facade --+--> new service
                   |    (/orders, /users)
                   +--> legacy system
                        (everything else)
```

The big-bang rewrite is the alternative, and it has a poor record: the old system keeps changing while you rebuild it, the rewrite delivers nothing until it is finished, and hidden behaviour in the old code is rediscovered as production bugs.

## Pitfalls

- **Refactoring without tests** is just editing and hoping.
- **Mixing refactoring with behaviour change** in one commit makes review and bisecting much harder. Separate commits, ideally separate PRs.
- **Refactoring for its own sake.** Spend effort where code changes often. A stable module may have little change-related cost, but still assess operational, security and knowledge risks.
- **Big-bang refactors on a long-lived branch** drift from main and end in painful merges. Prefer small steps merged daily.
- **Breaking public contracts.** Anything other code depends on (APIs, serialised formats, database schemas, even log formats parsed by alerts) is behaviour. Use parallel change.
- **Speculative generality.** Refactoring towards a flexibility nobody needs yet adds indirection. Refactor for the change in front of you.

## Key takeaways
- Refactoring changes structure, not behaviour, in small, verifiable steps. Do not mix it with feature or bug-fix work.
- Tests are the precondition. With legacy code, write characterisation tests that pin down current behaviour first.
- Code smells point you to likely problems; Extract, Rename, Move and Inline cover most daily work.
- For interfaces others depend on, use parallel change (expand, migrate, contract).
- For large components and systems, use branch by abstraction or the strangler fig instead of a big-bang rewrite.

## Further reading
- [Definition of Refactoring — Martin Fowler](https://martinfowler.com/bliki/DefinitionOfRefactoring.html)
- [Catalog of Refactorings — refactoring.com](https://refactoring.com/catalog/)
- [Workflows of Refactoring — Martin Fowler](https://martinfowler.com/articles/workflowsOfRefactoring/)
- [Parallel Change — Martin Fowler](https://martinfowler.com/bliki/ParallelChange.html)
- [Branch By Abstraction — Martin Fowler](https://martinfowler.com/bliki/BranchByAbstraction.html)
- [Strangler Fig Application — Martin Fowler](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [Code smell — Wikipedia](https://en.wikipedia.org/wiki/Code_smell)
