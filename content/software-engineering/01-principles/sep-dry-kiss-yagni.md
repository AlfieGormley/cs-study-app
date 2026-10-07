---
id: sep-dry-kiss-yagni
title: DRY, KISS, YAGNI and their limits
level: intermediate
minutes: 10
summary: What DRY, KISS and YAGNI actually say, why "duplication is cheaper than the wrong abstraction", the rule of three, and how to tell simple from merely easy.
---

Three short slogans shape a huge amount of everyday design argument. Each is useful. Each is also routinely misquoted, and the misquoted versions cause as much damage as the problems they were meant to prevent.

| Slogan | Expands to | Warns against |
|---|---|---|
| DRY | Don't repeat yourself | Scattered knowledge |
| KISS | Keep it simple | Needless complexity |
| YAGNI | You aren't gonna need it | Speculative features |

## DRY: it's about knowledge, not text

Andy Hunt and Dave Thomas coined DRY in *The Pragmatic Programmer* (1999):

> Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.

Note the word **knowledge**. DRY is not "never have two similar-looking lines of code". It is "never have two places that must be kept in step by hand".

### Real duplication

```python
# signup.py
if len(password) < 12:
    raise WeakPassword()

# reset.py
if len(password) < 10:
    raise WeakPassword()
```

There is one business rule ("minimum password length") with two representations, and they have already drifted apart. That is exactly what DRY targets:

```python
# passwords.py
MIN_LENGTH = 12

def check(password):
    if len(password) < MIN_LENGTH:
        raise WeakPassword()
```

DRY applies well beyond code: a database schema and an ORM model, an API and its documentation, a config value copied into three YAML files. Generating one from the other (or deriving both from a single source) keeps them in step.

### Accidental duplication

```python
def vat(price):
    return round(price * 0.2, 2)

def staff_discount(price):
    return round(price * 0.2, 2)
```

The code is identical, but the knowledge isn't. VAT is set by government; the staff discount is set by HR. They will change for different reasons at different times. Merging them into `twenty_percent(price)` couples two unrelated rules, and the first time one changes, someone adds a parameter to tell them apart.

> [!tip] The DRY question
> Don't ask "do these look the same?" Ask "if one of these changed, would the other *have* to change too?" Only a yes means duplication.

## The wrong abstraction

Sandi Metz's widely cited post puts it bluntly: **duplication is far cheaper than the wrong abstraction**. The lifecycle she describes:

1. A developer sees duplication and extracts a shared function.
2. A new requirement *almost* fits, so someone adds a parameter and an `if`.
3. Repeat. The function grows flags and branches serving different callers.
4. Nobody dares to touch it, because every caller depends on a different path.

```python
def export(rows, fmt, legacy=False,
           skip_header=False, eu=False,
           for_finance=False):
    ...
```

The fix she recommends is counter-intuitive: **inline the abstraction back into each caller**, delete the paths each caller doesn't use, and then look for the real shared idea, if there is one.

### The rule of three

A practical heuristic (attributed to Don Roberts and popularised in Fowler's *Refactoring*): the first time, just write it. The second time, wince but duplicate. The **third** time, refactor. By then you have three examples, which is usually enough to see what is truly common and what varies.

## KISS: simple is not the same as easy

Lockheed Martin associates "Keep it simple, stupid" with Kelly Johnson and the Skunk Works engineering approach.

In software, simplicity means **fewer concepts and fewer interactions** for a reader to hold in their head. It is not the same as "fewest lines" or "least typing".

```python
# Clever
def flatten(xs):
    return sum(map(lambda x: flatten(x)
               if isinstance(x, list)
               else [x], xs), [])
```

```python
# Simple
def flatten(xs):
    out = []
    for x in xs:
        if isinstance(x, list):
            out.extend(flatten(x))
        else:
            out.append(x)
    return out
```

The clever version is shorter, but a reader must untangle `sum` over lists, a lambda and a conditional expression. Even on a flat list of n elements it takes Θ(n²) time: `sum(..., [])` copies both operands each time. The recursive `extend` version avoids that flat-list penalty, although deep nesting still adds repeated copying and recursion overhead.

Rich Hickey's talk *Simple Made Easy* draws a useful line:

- **Easy** means familiar or close at hand ("I already know this framework").
- **Simple** means not intertwined: few parts, each doing one thing.

A heavyweight framework can be easy to start with and far from simple. A plain function and a dictionary can be unfamiliar to someone used to the framework, yet simple.

### Kent Beck's rules of simple design

In Fowler's presentation of Beck's rules, a simple design:

1. Passes the tests.
2. Reveals intention.
3. Has no duplication (of knowledge).
4. Has the fewest elements.

Correctness comes first and minimising elements comes last. Formulations differ on the middle two: Fowler notes that clarity and removing duplication usually reinforce one another; they are not a universally agreed tie-breaking order.

## YAGNI: build what you need now

Popularised in Extreme Programming: **don't build a capability until you actually need it**.

```python
# Requirement: export orders as CSV.

# YAGNI violation
class ExporterFactory:
    def create(self, fmt: str,
               plugin_dir=None):
        ...  # CSV, XML, Parquet, plugins

# Enough
def orders_to_csv(orders, file):
    writer = csv.writer(file)
    for o in orders:
        writer.writerow([o.id, o.total])
```

Martin Fowler breaks down what a presumptive feature costs, even when the guess turns out right:

- **Cost of build**: the time spent now.
- **Cost of delay**: the features you didn't ship because you were building this one.
- **Cost of carry**: every reader, test and change must work around the extra code.
- **Cost of repair**: when the guess is wrong, which it often is, the code must be ripped out or bent to fit.

### What YAGNI does not mean

- **It doesn't mean skip quality.** Fowler is explicit: YAGNI applies to *features*, not to refactoring, tests or clean structure that make the code easier to change. Those are what make deferring features safe.
- **It doesn't apply equally to things that are expensive to change later.** A public API, a wire format, a database schema shared by many services, or security: these deserve forethought because changing them later means migrations, versioning and coordinating other teams.

| Cheap to change: YAGNI | Costly to change: plan |
|---|---|
| Internal function | Public API or SDK |
| Private class layout | Event and file formats |
| One service's code | Shared database schema |
| UI wording | Auth and security model |

## When the principles collide

They regularly pull against each other:

- **DRY versus KISS.** Removing duplication between two 5-line functions by adding a generic, configurable helper can make the code *less* simple. Prefer the version a newcomer understands faster.
- **DRY versus decoupling.** Two microservices sharing a "common" library for their domain models can couple their evolution. Compatible, versioned releases can be adopted independently; a breaking shared-model change may instead force coordination. Duplicating a small DTO across a service boundary is often the right call.
- **YAGNI versus OCP.** OCP invites extension points; YAGNI says wait until there's a second case. The rule of three is a decent tie-breaker.
- **KISS versus performance.** The simplest code is sometimes too slow. Optimise where measurement says it matters, and keep the complexity contained there.

## Key takeaways
- DRY is about knowledge: one authoritative place for each fact or rule. Similar-looking code that changes for different reasons is not duplication.
- Duplication is cheaper than the wrong abstraction; if a shared function is sprouting flags, inline it and start again.
- The rule of three: refactor on the third occurrence, when the pattern is clear.
- KISS means fewer intertwined concepts, not fewer lines; simple is not the same as easy.
- YAGNI applies to speculative features, not to tests and refactoring, and is weaker for decisions that are expensive to reverse (public APIs, data formats, security).
- The principles conflict; resolve conflicts in favour of whatever makes the next change cheapest.

## Further reading
- [Don't repeat yourself — Wikipedia](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)
- [The Wrong Abstraction — Sandi Metz](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)
- [Yagni — Martin Fowler](https://martinfowler.com/bliki/Yagni.html)
- [Beck Design Rules — Martin Fowler](https://martinfowler.com/bliki/BeckDesignRules.html)
- [KISS principle — Wikipedia](https://en.wikipedia.org/wiki/KISS_principle)
- [Rule of three (computer programming) — Wikipedia](https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming))
