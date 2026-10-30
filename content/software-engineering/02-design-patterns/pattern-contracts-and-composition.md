---
id: pattern-contracts-and-composition
title: Contracts and composition
level: basic
minutes: 4
sourceLesson: pattern-why
summary: Depend on the behaviour an object promises, including the meaning of its arguments.
---

## The two principles underneath

Two principles from the book's introduction run through much of the catalogue. Not every pattern follows both: factory method and template method deliberately use subclassing.

### Program to an interface, not an implementation

Code should depend on *what an object can do*, not *which class it is*. If a report generator accepts "anything with a `write(text)` method", you can hand it a text file, a socket adapter exposing that contract, an in-memory text buffer or a test fake. A raw socket does not provide write(text).

In Python this is **duck typing**. You can make it explicit with an abstract base class or a `typing.Protocol`, but the idea is the same.

### Favour object composition over class inheritance

Inheritance fixes the base-class relationship when a class is defined and can couple a subclass to its parent’s implementation. Inherited methods can still inspect mutable state or use dynamic dispatch at run time. Composition lets you assemble and replace collaborator objects at run time.

Here is the classic way inheritance goes wrong:

```
         Notifier
        /    |    \
    Email   SMS   Slack
     /  \
 Email+  Email+
 Retry   Log      ... and so on
```

Every combination of channel and features needs its own subclass. Each optional feature is either on or off, so every new feature doubles the number of possible feature sets per channel. With 3 channels and 3 features (retry, logging, rate limiting), that is up to 24 subclasses, and a fourth feature takes it to 48.

With composition you write each channel once and each feature once, as a wrapper, and combine them at run time. The same system needs 6 classes, and a fourth feature adds just one more. Inheritance *multiplies* the parts; composition *adds* them.

Those inheritance figures are a worst case: they assume every combination is wanted and each gets its own class. Real teams usually stop at a handful, but each new combination still means a new class. That pressure is why the GoF said to favour composition. Here is the composition version in code:

```python
class Email:
    def send(self, msg):
        print(f"email: {msg}")

class Retry:
    def __init__(self, inner, tries=3):
        # Exclude booleans as retry counts.
        valid = type(tries) is int
        if not valid or tries < 1:
            raise ValueError("tries > 0")
        self.inner = inner
        self.tries = tries

    def send(self, msg):
        for n in range(self.tries):
            try:
                # A successful send ends
                # retries.
                return self.inner.send(msg)
            except ConnectionError:
                # Preserve the final
                # failure.
                if n == self.tries - 1:
                    raise

notifier = Retry(Email())
notifier.send("deploy finished")
# prints: email: deploy finished
```

`Retry` works with any object that has `send`, so one class serves every channel. That is the decorator pattern, which is covered in the later short lesson on stacking decorators.

## Key takeaways
- Depend on the behaviour an object promises, including the meaning of its arguments.
- Composition combines channel and feature objects without one subclass for every combination.
- The subclass counts assume every combination exists; wrapper order and compatible contracts still matter.

## Further reading
- [Design Patterns — publisher catalogue](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-software-9780201633610)
- [abc — Python documentation](https://docs.python.org/3/library/abc.html)
