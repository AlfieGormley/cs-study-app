---
id: pattern-swappable-strategies
title: Swapping algorithms as values
level: intermediate
minutes: 3
sourceLesson: pattern-behavioural-1
summary: A strategy isolates an interchangeable algorithm behind a common contract.
---

Behavioural patterns are about **who does what** and **how objects talk**. They move decisions and messages around so that the parts that change often are separated from the parts that don't.

These three neighbouring short lessons cover different kinds of variation:

- **Strategy pattern** turns *an algorithm* into a value you can swap.
- **Observer pattern** turns *"something happened"* into a notification any number of listeners can receive.
- **Command pattern** turns *a request* into an object you can store, queue, log or undo.

All three are partly built into Python, because functions and closures are first-class values.

## Strategy pattern

### The problem

A piece of code needs one of several interchangeable algorithms: pricing rules, compression codecs, retry policies, sort orders. Hard-coding them as an `if/elif` chain means editing (and retesting) the core every time a new one appears.

### The structure

```
  Context -----------> Strategy
  +strategy           +run(data)
  +do(): uses it        ^     ^
                        |     |
                     FastA   CheapB
```

The context holds a strategy and delegates the varying step to it. Callers pick which strategy to give it.

### In Python

Java can use lambdas or method references for functional-interface strategies; Python commonly passes a function directly:

```python
def flat(total):
    return total

def ten_off(total):
    return total * 0.9

def bulk(total):
    # Keep the threshold inside this rule.
    if total > 50:
        return total - 5
    return total

def checkout(items, pricing=flat):
    # The caller chooses the pricing rule.
    return pricing(sum(items))

print(checkout([30, 40]))           # 70
print(checkout([30, 40], ten_off))  # 63.0
print(checkout([30, 40], bulk))     # 65
```

If a strategy needs configuration, use a closure, `functools.partial`, or a small class with `__call__`. If it needs several related methods (say, `encode` *and* `decode`), a class with those methods is clearer than a pair of functions.

> [!tip] Replace the `if` chain with a dict
> `PRICING = {"flat": flat, "sale": ten_off}` then `PRICING[name](total)` is strategy plus a lookup table. Adding a rule is one new function and one dict entry.

### When not to use it

- When there's only one algorithm and no real prospect of another.
- When strategies need very different inputs. A shared signature that has to carry everything any strategy might want is a sign the abstraction is wrong.
- When callers shouldn't be choosing. Exposing a strategy parameter is a public commitment you'll have to support.

### In real libraries

- **`sorted(key=...)`, `max(key=...)`, `min(key=...)`**: the comparison key is a strategy.
- **`json.dumps(default=..., cls=...)`**: plug in how unknown types are serialised.
- **Django's `PASSWORD_HASHERS`**: a list of hasher classes (PBKDF2, Argon2, bcrypt and so on) with a common interface. The first is used for new passwords; the rest can still verify old ones.
- **requests' `auth=`**: pass `HTTPBasicAuth`, `HTTPDigestAuth` or your own callable that modifies the request.
- **Java's `Comparator`**, and **scikit-learn**, where any estimator with `fit` and `predict` can be dropped into the same code.

## Key takeaways
- A strategy isolates an interchangeable algorithm behind a common contract.
- Functions, partials and callable objects are idiomatic Python strategy forms.
- Do not force incompatible inputs into an artificially broad common signature.

## Further reading
- [Sorting techniques — Python documentation](https://docs.python.org/3/howto/sorting.html)
- [functools — Python documentation](https://docs.python.org/3/library/functools.html)
- [Advanced usage — Requests documentation](https://requests.readthedocs.io/en/latest/user/advanced/)
