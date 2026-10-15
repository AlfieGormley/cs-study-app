---
id: pattern-template-hooks
title: Template methods and overridable hooks
level: advanced
minutes: 3
sourceLesson: pattern-behavioural-2
summary: A template method fixes the overall algorithm and delegates variable steps.
---

## Template Method pattern

### The problem

Several classes share the same overall algorithm but differ in a few steps. You want the skeleton written once, with the steps filled in by subclasses.

### The structure

```
 AbstractClass
 +run():           (fixed skeleton)
   self.setup()
   self.step()     <- must override
   self.teardown()
       ^
       |
 ConcreteClass: step(), maybe setup()
```

The base class calls the subclass, not the other way round. This is sometimes called the **Hollywood principle**: "don't call us, we'll call you".

### In Python

```python
class Report:
    def render(self):
        # The base method keeps the
        # sequence;
        # overrides supply individual steps.
        parts = [self.header()]
        parts += [self.row(r)
                  for r in self.rows()]
        parts.append(self.footer())
        return "\n".join(parts)

    def header(self):
        return "REPORT"

    def footer(self):
        return "END"

    def rows(self):
        raise NotImplementedError

    def row(self, r):
        return str(r)

class Sales(Report):
    def rows(self):
        return [120, 80]

    def row(self, r):
        return f"£{r}"

print(Sales().render())
# REPORT
# £120
# £80
# END
```

Steps with a default (`header`, `row`) are optional **hook methods**; `rows` is required. Mark required steps with `@abc.abstractmethod` if you want instantiation to fail fast when one is missing.

### When not to use it

- When subclasses would override most of the steps. The "shared skeleton" isn't really shared.
- When you need to vary steps independently and combine them. Inheritance gives one fixed combination per subclass; strategy objects passed in can be mixed freely.
- Deep hierarchies make template methods hard to follow: reading `render()` doesn't tell you which `row()` will run.

### In real libraries

- **`unittest.TestCase`**: `run()` normally calls setUp, the test and tearDown; tearDown is not run if setUp fails. Cleanup registered with addCleanup has separate guarantees.
- **`socketserver.BaseRequestHandler`**: after successful `setup()`, its constructor calls `handle()` and guarantees `finish()` via `finally`; if `setup()` raises, `finish()` is not called. You override `handle()`.
- **`threading.Thread`**: `start()` arranges for `run()` to be called on a new thread; you override `run()`.
- **Django's class-based views**: `dispatch()` routes to `get()` or `post()`, which you override.
- **`collections.abc.Mapping`**: implement `__getitem__`, `__iter__` and `__len__`, and you inherit `get`, `keys`, `items`, `__contains__` and more, all written in terms of those three.

## Key takeaways
- A template method fixes the overall algorithm and delegates variable steps.
- Lifecycle guarantees depend on which earlier step succeeds.
- Use composition when independently varying steps would multiply subclasses.

## Further reading
- [unittest — Python documentation](https://docs.python.org/3/library/unittest.html)
- [socketserver — Python documentation](https://docs.python.org/3/library/socketserver.html)
