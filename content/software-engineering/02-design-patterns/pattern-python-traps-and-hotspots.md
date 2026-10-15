---
id: pattern-python-traps-and-hotspots
title: Python traps and refactoring priorities
level: advanced
minutes: 3
sourceLesson: pattern-anti-patterns
summary: Mutable defaults are shared between calls unless the function creates a fresh value.
---

## Python-specific traps

A few anti-patterns are specific to Python:

- **Mutable default arguments.** `def add(x, items=[])` creates the list *once*, when the function is defined, and shares it across calls.
- **Swallowing exceptions.** `except Exception: pass` hides bugs; a bare `except:` also catches `KeyboardInterrupt` and `SystemExit`.
- **`from module import *`** hides the origin of imported names at their use sites, and later imports silently shadow earlier ones.

```python
# Deliberate bug: one list for all calls.
def add(x, items=[]):
    items.append(x)
    return items

print(add(1))   # [1]
print(add(2))   # [1, 2]  shared list!

def add_ok(x, items=None):
    # Omitted argument gets a new list;
    # an explicitly supplied list is reused.
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
- Mutable defaults are shared between calls unless the function creates a fresh value.
- Exception handling and imports should keep failures and name origins visible.
- Prioritise change-heavy complex areas while also considering risk, defects and team experience.

## Further reading
- [Default argument values — Python tutorial](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values)
- [Hotspots — CodeScene documentation](https://docs.enterprise.codescene.io/versions/7.2.0/guides/technical/hotspots.html)
- [Anti-pattern — Wikipedia](https://en.wikipedia.org/wiki/Anti-pattern)
- [Big Ball of Mud — Brian Foote and Joseph Yoder](https://www.laputan.org/mud/)
- [Strangler Fig Application — Martin Fowler](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [Anemic Domain Model — Martin Fowler](https://martinfowler.com/bliki/AnemicDomainModel.html)
- [Inversion of Control Containers and the Dependency Injection pattern — Martin Fowler](https://martinfowler.com/articles/injection.html)
- [Code smells catalogue — Refactoring.Guru](https://refactoring.guru/refactoring/smells)
