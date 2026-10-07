---
id: sep-clean-code
title: Clean code: naming and functions
level: basic
minutes: 9
summary: Why readable code matters, how to choose names that carry meaning, and how to shape functions that do one thing at one level of abstraction.
---

Code is written once and read many times: by reviewers, by the on-call engineer at 3 a.m., by you in six months. Every minute a reader spends working out what `d` or `process()` means is a minute not spent on the actual problem.

"Clean code" is not about elegance for its own sake. It is about lowering the cost of the next change. Most of that cost comes from two things you control on every line: **names** and **functions**.

## Why readability is an economic argument

A program that works but is hard to read is like a house with no labels on the fuse box. It's fine until something goes wrong.

- **Reading dominates.** Before you change a line, you read the code around it, its callers and its tests. The exact ratio varies by task; no measured ratio is established here.
- **Bugs hide in confusion.** If a reviewer can't tell what a function is meant to do, they can't tell whether it does it.
- **Design stamina.** Martin Fowler's *design stamina hypothesis* proposes that investing in structure can repay its initial cost through easier later changes. His suggested payoff after weeks is explicitly a judgment, not a measured universal crossover.

Clean code is a property of the reader's experience, so the test is simple: can a competent colleague who has never seen this code understand it quickly and change it safely?

## Naming

A name is the smallest unit of documentation. It is read every time the code is read, and it never goes out of date as quietly as a comment does.

### Reveal intent

Compare:

```python
def calc(d, r):
    return d * (1 - r)
```

```python
def discounted_price(price, discount_rate):
    return price * (1 - discount_rate)
```

The second version needs no comment. The reader knows what goes in, what comes out, and roughly what happens.

### Put units and meaning in the name

Ambiguous units cause real failures. NASA's Mars Climate Orbiter was lost in 1999 because one piece of software produced pound-force seconds and another expected newton seconds.

```python
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
- **Avoid encodings.** Hungarian notation (`strName`) duplicates what the type system and editor already tell you.
- **Use the domain's language.** If the business says "policy holder", don't call it `customer` in the code.

### Magic numbers

A bare literal forces readers to guess its meaning and makes changes error-prone.

```python
# Before
if attempts > 5:
    lock(account)
time.sleep(86400)

# After
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT = timedelta(days=1)

if attempts > MAX_LOGIN_ATTEMPTS:
    lock(account)
time.sleep(LOCKOUT.total_seconds())
```

Not every literal is magic: `0`, `1`, and `len(x) - 1` are usually clear in context.

## Functions

### Do one thing

A function should do one thing, do it well, and do only that. A practical test: can you describe it in one sentence without "and"? If you can extract a meaningful sub-function from it with a name that isn't just a restatement, it was doing more than one thing.

Fowler offers a sharper rule: **separate intention from implementation**. If you have to read a block of code to work out *what* it does, extract it into a function named after the what. Then the length of the function matters much less than whether its name tells the truth.

### One level of abstraction

Mixing high-level steps with low-level detail makes a function hard to skim.

```python
# Before: three levels of detail mixed
def checkout(cart, user):
    total = 0
    for item in cart.items:
        total += item.price * item.qty
    if user.country == "GB":
        total *= 1.2
    conn = psycopg.connect(DSN)
    conn.execute(
        "INSERT INTO orders ...", (total,))
    smtplib.SMTP("mail").sendmail(...)
```

```python
# After: reads like a summary
def checkout(cart, user):
    total = add_tax(cart.subtotal(), user)
    order = orders.save(user, total)
    notifier.order_placed(order)
    return order
```

These checkout fragments illustrate organisation; the tax rule and service calls are placeholders, not a complete tax or transaction implementation. The "after" version tells a story at one altitude. The details still exist, but each lives in a function where it is the main subject.

### Few parameters, no flag arguments

Each parameter is something a caller must understand and get right. Three positional parameters of the same type are an accident waiting to happen:

```python
transfer(100, 42, 17)  # which is which?
```

Python's keyword-only arguments help:

```python
def transfer(*, amount, src, dst): ...

transfer(amount=100, src=42, dst=17)
```

A **flag argument** (a boolean that changes what the function does) is a sign the function does two things:

```python
render(doc, True)       # True what?

# Prefer two named functions
render_preview(doc)
render_print(doc)
```

When many parameters always travel together (`street, city, postcode`), introduce a **parameter object** (`Address`).

### Command-query separation

Bertrand Meyer's rule: a function should either **do something** (a command, which changes state) or **answer something** (a query, which returns data without side effects), not both.

```python
# Surprising: a "check" that mutates
def is_valid(order):
    order.validated_at = now()
    return order.total > 0
```

A reader calling `if is_valid(order):` does not expect state to change. Hidden side effects are among the most expensive bugs to find, because nothing in the call site hints at them. (Some exceptions are idiomatic, like `stack.pop()`, which removes and returns.)

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
# After
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
# After
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
- Code is read far more than it is written; optimise for the reader.
- Names should reveal intent, carry units, scale with scope and use the domain's vocabulary.
- Replace magic numbers with named constants or types.
- Functions should do one thing at one level of abstraction; extract when a name explains a block better than its code.
- Avoid flag arguments and long positional parameter lists; use keyword-only arguments and parameter objects.
- Keep commands and queries separate, and prefer guard clauses to deep nesting.

## Further reading
- [PEP 8: Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Function Length — Martin Fowler](https://martinfowler.com/bliki/FunctionLength.html)
- [Flag Argument — Martin Fowler](https://martinfowler.com/bliki/FlagArgument.html)
- [Command Query Separation — Martin Fowler](https://martinfowler.com/bliki/CommandQuerySeparation.html)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Code smells catalogue — Refactoring.Guru](https://refactoring.guru/refactoring/smells)
