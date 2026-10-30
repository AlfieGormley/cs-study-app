---
id: sep-names-and-units
title: Names that carry intent and units
level: basic
minutes: 5
summary: Name booleans as questions and use the domain vocabulary.
sourceLesson: sep-clean-code
---

Code is written once and read many times: by reviewers, by the on-call engineer at 3 a.m., by you in six months. Every minute a reader spends working out what `d` or `process()` means is a minute not spent on the actual problem.

"Clean code" is not about elegance for its own sake. It is about lowering the cost of the next change. Most of that cost comes from two things you control on every line: **names** and **functions**.

## Why readability is an economic argument

A program that works but is hard to read is like a house with no labels on the fuse box. It's fine until something goes wrong.

- **Reading dominates.** Before you change a line, you read the code around it, its callers and its tests. The exact ratio varies by task; no measured ratio is established here.
- **Bugs hide in confusion.** If a reviewer can't tell what a function is meant to do, they can't tell whether it does it.
- **Design stamina.** Martin Fowler's *design stamina hypothesis* proposes that investing in structure can repay its initial cost through easier later changes. His suggested payoff after weeks is explicitly a judgment, not a measured universal crossover.

Clean code is a property of the reader's experience, so the test is simple: can a competent colleague who has never seen this code understand it quickly and change it safely?

The naming advice below collects widely used conventions from style guides such as PEP 8 and books such as Robert C. Martin's *Clean Code*. Treat them as heuristics: an established team convention usually beats a rule applied in isolation.

## Naming

A name is the smallest unit of documentation. It is read every time the code is read, and it never goes out of date as quietly as a comment does.

### Reveal intent

Compare:

```python
# Apply the remaining fraction to d.
def calc(d, r):
    return d * (1 - r)
```

```python
# Keep the calculation; expose its meaning.
def discounted_price(price, discount_rate):
    return price * (1 - discount_rate)
```

The second version needs no comment. The reader knows what goes in, what comes out, and roughly what happens.

### Put units and meaning in the name

Ambiguous units cause real failures. NASA's Mars Climate Orbiter was lost in 1999 because one piece of software produced pound-force seconds and another expected newton seconds. One pound-force second is about 4.45 newton seconds, so the navigation software underestimated the effect of each small thruster firing by that factor.

```python
# Both values use the same numeric type.
timeout = 30          # seconds? ms?
timeout_seconds = 30  # unambiguous
```

Better still, use a type that carries the unit, such as Python's `datetime.timedelta(seconds=30)`.

### Name length should match scope

A loop index used for two lines can be `i`. A module-level constant used across a codebase deserves a full name. The wider the scope, the more context a reader has lost by the time they meet the name, so the name must carry more.

| Scope | Example |
|---|---|
| 2-line loop | `i`, `row` |
| Function | `unpaid_invoices` |
| Module/global | `MAX_LOGIN_ATTEMPTS` |

### Other naming rules that pay off

- **Booleans read as predicates**: `is_active`, `has_permission`, `should_retry`. Avoid `flag` or `status`.
- **Functions are verbs, values are nouns**: `send_invoice()`, `invoice`.
- **One word per concept.** Don't use `fetch`, `get` and `retrieve` for the same idea in one codebase; readers will assume they differ.
- **Avoid noise words**: `data`, `info`, `manager`, `handle`. `UserData` versus `User` tells the reader nothing extra.
- **Avoid encodings.** Type-encoding prefixes such as `strName` often duplicate what the type system and editor already tell you. Hungarian notation is a broader family of conventions: semantic prefixes that distinguish units or kinds are a different design choice.
- **Use the domain's language.** If the business says "policy holder", don't call it `customer` in the code.

### Magic numbers

A bare literal forces readers to guess its meaning and makes changes error-prone.

```python
# Before: what do 5 and 86400 mean?
if attempts > 5:
    lock(account, 86400)

# After: names carry meaning and units
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT = timedelta(days=1)

if attempts > MAX_LOGIN_ATTEMPTS:
    lock(account, LOCKOUT)
```

`lock` stands for whatever records the lockout. The rule is unchanged: the threshold is still 5 and the lockout still lasts one day (86,400 seconds), but the reader no longer has to work that out. In the "after" version `lock` receives a `timedelta` rather than a bare number of seconds, so the unit travels with the value.

Not every literal is magic: `0`, `1`, and `len(x) - 1` are usually clear in context.

## Key takeaways
- Name booleans as questions and use the domain vocabulary.
- Include units or use a unit-bearing type when a number could be misread.
- Give wider-scope identifiers enough context and replace unexplained literals.

## Further reading
- [PEP 8: Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [NASA: Mars Climate Orbiter mission page](https://science.nasa.gov/mission/mars-climate-orbiter/)
- [Martin Fowler: Design Stamina Hypothesis](https://martinfowler.com/bliki/DesignStaminaHypothesis.html)
