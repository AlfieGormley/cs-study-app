---
id: pattern-anti-patterns
title: Anti-patterns
level: advanced
minutes: 15
summary: The recurring bad solutions, from god objects and big balls of mud to golden hammers, lava flows, singleton abuse and pattern overuse, why sensible teams fall into them, how to spot them, and how to climb back out.
---

A pattern is a recurring *good* solution. An **anti-pattern** is a recurring *bad* one: a response to a real problem that looks reasonable at the time, keeps getting used, and produces worse consequences than it solves.

That second part matters. An anti-pattern isn't just a mistake. It's an attractive mistake, which is why it recurs, and it usually has a known better alternative.

The term was coined by Andrew Koenig in 1995 and popularised by the 1998 book *AntiPatterns* by Brown, Malveau, McCormick and Mowbray. Closely related are Martin Fowler and Kent Beck's **code smells** from *Refactoring* (1999): surface symptoms that often point to a deeper problem.

## Why good teams produce bad structure

Anti-patterns rarely come from ignorance. They come from **local decisions that are each reasonable**:

- "Just add it to `OrderService` for now; we'll split it later."
- "Copy this function and tweak it; the deadline is Friday."
- "Nobody knows what this does, so don't touch it."

Each step saves time today and adds a little cost to every future change. The costs compound, which is why Ward Cunningham's **technical debt** metaphor fits so well.

## God object

### What it looks like

One class knows and does far too much. `OrderManager` validates input, calculates prices, talks to the database, sends emails, formats PDFs and holds global caches. The *AntiPatterns* book calls it **the Blob**.

```
          +--------------+
 UI ----> |              | ----> DB
 API ---> | OrderManager | ----> Email
 Jobs --> |  4,000 lines | ----> PDF
 Tests -> |  90 methods  | ----> Cache
          +--------------+
```

### Why it happens

There's always one obvious place to put the next feature, and adding a method there is faster than designing a new class.

### Why it hurts

- Every change risks breaking an unrelated feature.
- It's a merge-conflict magnet, since everyone edits the same file.
- It's hard to test: constructing one needs every dependency.
- Low cohesion and high coupling at the same time.

### The way out

Extract classes along responsibility lines (pricing, notification, persistence), one at a time, with tests around each extraction. The **single responsibility principle** is the test: how many unrelated reasons does this class have to change?

## Big ball of mud

Brian Foote and Joseph Yoder named it in 1997: a system that is "haphazardly structured, sprawling, sloppy, duct-tape and bailing wire, spaghetti code jungle". It's the god object at the scale of a whole system: no discernible architecture, everything depending on everything.

Their paper is unusually sympathetic. It calls the big ball of mud the de facto standard software architecture, because it is what you get from deadlines, staff turnover and growth without investment in structure. Sometimes it's even the right economic choice for throwaway code.

### The way out

Rewriting from scratch is tempting and usually a mistake: the rewrite has to rediscover years of edge cases while the old system keeps changing. The usual alternative is the **strangler fig** approach (named by Martin Fowler): put a routing layer in front, build new functionality beside the old system, move features across one at a time, and retire the old code as it empties.

## Golden hammer

As the saying goes, if all you have is a hammer, everything looks like a nail (Abraham Maslow put it this way in 1966). A team that knows one tool well applies it to every problem: every data store is Postgres, every integration is Kafka, every problem is solved with microservices, or every design gets an abstract factory.

Familiar tools *are* valuable (operational knowledge counts for a lot), so the question is whether the fit is genuinely good or just familiar. Warning signs: workarounds piling up to make the tool fit, and nobody on the team able to name what the alternative would be.

## Lava flow

Dead or half-finished code from past experiments, which has hardened in place because nobody is sure it's safe to remove. You'll see comments like `# TODO: remove after migration (2019)`, unused feature flags, and classes with no callers that still get "maintained".

```python
def price(order):
    # v1 pricing, DO NOT DELETE
    # (needed by legacy export?)
    if settings.LEGACY_PRICING:
        return _old_price(order)
    return _new_price(order)
```

### The way out

Committed code remains recoverable while its history is retained. Use callers, configuration, representative production telemetry and owner knowledge to build evidence that a branch is unused; an observation window with zero hits is not proof that rare or scheduled paths never need it. Give every feature flag an owner and an expiry date.

## Copy-and-paste programming and shotgun surgery

Copying a block and tweaking it is the fastest way to get the second variant working. By the fifth copy, a bug fix has to be found and applied five times, and one copy will be missed.

The related smell is **shotgun surgery**: one conceptual change (say, adding a currency) requires small edits across many files. It means knowledge about one concept is spread out instead of being in one place.

> [!tip] Rule of three
> Duplication twice is often fine; abstracting too early guesses at the wrong shape. On the third occurrence, the common shape is usually clear, so extract it then.

## Magic numbers and primitive obsession

```python
if user.status == 3 and amount > 9999:
    fee = amount * 0.029 + 20
```

What's status 3? Why 9999? Is 20 pence or pounds? **Magic numbers** hide meaning; named constants or enums restore it.

**Primitive obsession** is the wider smell: representing domain concepts as raw strings, ints and floats. Money as a float invites rounding errors (`0.1 + 0.2 != 0.3`); an email as a `str` means validation is repeated, or forgotten, everywhere. A small type (`Money` built on `Decimal`, an `Email` value object) puts the rules in one place.

## Singleton abuse and service locator

Lesson 2 covered why singletons are hidden global state. The anti-pattern is using them as a way to avoid passing dependencies around: `Config.instance()`, `Db.instance()` and `Cache.instance()` reached for from anywhere.

**Service locator** is its more sophisticated cousin: a global registry you ask for dependencies (`locator.get(PaymentGateway)`). It's flexible, but dependencies obtained this way are hidden inside method bodies. Mark Seemann famously argued that it's an anti-pattern for this reason. The alternative is **dependency injection**: pass dependencies in through the constructor, so they're visible and replaceable.

## Anaemic domain model

Martin Fowler's term (2003) for domain objects that are just bags of getters and setters, with all the business rules living in separate "service" classes. You get the cost of an object model (mapping, classes) without the benefit (behaviour next to the data it protects), and invariants can be broken from anywhere.

This one is contested. In data-pipeline or CRUD-heavy code, plain data plus functions is often the clearest design, and functional programmers would argue it's the right default. It becomes a problem when there are real business rules that keep being re-implemented, or violated, outside the objects.

## Pattern overuse

The anti-pattern this module most needs to warn about: **using patterns because they exist**.

```python
class GreeterFactory:
    def create(self):
        return EnglishGreeter()

class EnglishGreeter:
    def greet(self, name):
        return f"Hello, {name}"

g = GreeterFactory().create()
print(g.greet("Ada"))
```

That is two classes and a factory for what is really `f"Hello, {name}"`. Signs of patternitis:

- Interfaces with one implementation and no test double.
- Factories that only ever create one class.
- Layers that only forward calls.
- Class names built from pattern names (`AbstractStrategyFactoryProvider`).

The fix is to inline the indirection until a second real variant arrives.

## Python-specific traps

A few anti-patterns are specific to Python:

- **Mutable default arguments.** `def add(x, items=[])` creates the list *once*, when the function is defined, and shares it across calls.
- **Swallowing exceptions.** `except Exception: pass` hides bugs; a bare `except:` also catches `KeyboardInterrupt` and `SystemExit`.
- **`from module import *`** makes it impossible to tell where names come from, and later imports silently shadow earlier ones.

```python
def add(x, items=[]):
    items.append(x)
    return items

print(add(1))   # [1]
print(add(2))   # [1, 2]  shared list!

def add_ok(x, items=None):
    items = [] if items is None else items
    items.append(x)
    return items
```

## Finding them in a real codebase

You can't fix everything, so find where it hurts most:

1. **Hotspots.** Files that are both complex *and* frequently changed are where anti-patterns cost the most. `git log --format= --name-only | sort | uniq -c | sort -rn` gives change frequency; combine it with file size or a complexity score. Adam Tornhill's *Your Code as a Crime Scene* builds a whole method on this.
2. **Change coupling.** Files that always change together in commits but live far apart signal shotgun surgery.
3. **Team pain.** Where do bugs cluster? Which file does nobody want to touch?

Then refactor in small, tested steps, as part of feature work in that area, rather than as a big-bang clean-up.

## Key takeaways
- An anti-pattern is a recurring, attractive solution whose consequences outweigh its benefits, and which has a known better alternative.
- They come from locally reasonable shortcuts whose costs compound over time.
- God objects and big balls of mud are fixed incrementally: extract responsibilities one at a time, or strangle the old system rather than rewriting it.
- Golden hammers, lava flows, copy-paste, magic numbers and primitive obsession each hide knowledge or spread it around.
- Singleton abuse and service locators hide dependencies; inject them instead.
- Overusing patterns is itself an anti-pattern; add indirection only when real variation appears.
- Prioritise by hotspots: code that is both complex and frequently changed.

## Further reading
- [Anti-pattern — Wikipedia](https://en.wikipedia.org/wiki/Anti-pattern)
- [Big Ball of Mud — Brian Foote and Joseph Yoder](https://www.laputan.org/mud/)
- [Strangler Fig Application — Martin Fowler](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [Anemic Domain Model — Martin Fowler](https://martinfowler.com/bliki/AnemicDomainModel.html)
- [Inversion of Control Containers and the Dependency Injection pattern — Martin Fowler](https://martinfowler.com/articles/injection.html)
- [Code smells catalogue — Refactoring.Guru](https://refactoring.guru/refactoring/smells)
