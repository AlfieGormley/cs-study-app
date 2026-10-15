---
id: pattern-contracts-and-composition
title: Contracts and composition
level: basic
minutes: 4
sourceLesson: pattern-why
summary: Depend on the behaviour an object promises, including the meaning of its arguments.
---

## The two principles underneath

Almost every GoF pattern is an application of two principles stated in the book's introduction.

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

Every combination of feature and channel needs its own subclass. To see how fast that grows, count the combinations. Each optional feature is either switched on or off, so every extra feature doubles the number of possible feature sets. Multiply by the number of channels and you get the worst-case class count:

```formula
N_inherit = c(2^f)
N_inherit = 3 × 2^3
N_inherit = 3 × 8 = 24
where
N_inherit: the number of concrete subclasses needed when every combination of one channel and a set of features gets its own class (a plain count, no unit)
c: the number of channels, such as email, SMS and Slack; here 3
f: the number of optional features, such as retry, logging and rate limiting, each of which can be on or off independently; here 3
2^f: f copies of 2 multiplied together; it counts the possible on/off feature sets, including the set with no features at all (2^3 = 2 × 2 × 2 = 8)
In words: each channel needs one subclass for every possible set of features, so the class count doubles every time you add a feature.
```

With composition you write each channel once and each feature once, as a wrapper, and combine them at run time:

```formula
N_compose = c + f
N_compose = 3 + 3 = 6
where
N_compose: the number of classes you write when channels and features are separate, combinable classes (a plain count, no unit)
c: the number of channels; here 3
f: the number of optional features, each written once as a wrapper class; here 3
In words: with composition the class count only adds up, one class per channel plus one per feature.
```

Add a fourth feature and the gap widens fast: inheritance needs 3 × 16 = 48 subclasses, composition needs 3 + 4 = 7 classes. The 24 is a worst case ("up to"): it assumes every combination is actually used and that each one is a separate class. In practice teams stop at a handful of combinations, but the pressure towards this explosion is why the GoF said to favour composition. Here is the composition version in code:

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
