---
id: sep-effects-guards-refactoring
title: Preserve behaviour when making code clearer
level: basic
minutes: 3
summary: A query should not hide a state change.
sourceLesson: sep-clean-code
---

Making code clearer is only safe if callers see exactly the same behaviour afterwards. This lesson covers two clarity techniques and the trap each one hides.

### Command-query separation

Bertrand Meyer's rule: a function should either **do something** (a command function, which changes state) or **answer something** (a query function, which returns data without side effects), not both.

```python
# Surprising: a "check" that mutates
def is_valid(order):
    order.validated_at = now()
    return order.total > 0
```

A reader calling `if is_valid(order):` does not expect state to change. Hidden side effects are hard to find, because nothing in the call site hints at them. (Some exceptions are idiomatic, like `stack.pop()`, which removes and returns.)

### Prefer guard clauses to deep nesting

```python
# Before
def ship(order):
    if order is not None:
        if order.paid:
            if order.items:
                dispatch(order)
```

```python
# After: same three rejections
def ship(order):
    if order is None:
        return
    if not order.paid:
        return
    if not order.items:
        return
    dispatch(order)
```

Each guard deals with one special case and gets out of the way, leaving the "happy path" unindented at the bottom.

## A worked refactor

```python
# Before
def proc(l):
    r = []
    for x in l:
        if x[2] == 1 and x[3] > 18:
            r.append(x[0] + " " + x[1])
    return r
```

Problems: meaningless names (`proc`, `l`, `r`, `x`), magic indices (`x[2]`), a magic number (`1` meaning "active"?), and the reader must decode the condition.

```python
# After: still > 18, deliberately
from dataclasses import dataclass

ADULT_AGE = 18

@dataclass
class Member:
    first: str
    last: str
    active: bool
    age: int

def adult_member_names(members):
    return [
        f"{m.first} {m.last}"
        for m in members
        if m.active and m.age > ADULT_AGE
    ]
```

Note a subtle question this refactor surfaces: is an 18-year-old an adult? The original said `> 18`. Clean names make such bugs *visible*; whether to fix it is a separate, deliberate change.

## Pitfalls and limits

- **Over-extraction.** Ten three-line functions that each call the next can be harder to follow than one clear twenty-line function. Extract when the name adds information.
- **Consistency beats preference.** Follow the codebase's existing conventions (and [PEP 8](https://peps.python.org/pep-0008/) in Python) even if you'd choose differently. Mixed styles cost more than either style.
- **Renaming has a cost** in public APIs, where callers you can't see depend on the name. Inside a module, editor refactoring tools can help, but check dynamic references, configuration and tests before treating a rename as safe.
- **Clean is not clever.** A one-line nested comprehension that replaces a readable loop is not cleaner.

## Key takeaways
- A query should not hide a state change.
- Guard clauses must preserve the original conditions, not merely flatten indentation.
- Naming can expose a boundary bug; fix that separately from a behaviour-preserving refactor.

## Further reading
- [Martin Fowler: Command Query Separation](https://martinfowler.com/bliki/CommandQuerySeparation.html)
- [Refactoring catalogue](https://refactoring.com/)
- [PEP 8: Style Guide for Python Code](https://peps.python.org/pep-0008/)
