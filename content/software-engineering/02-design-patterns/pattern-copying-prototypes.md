---
id: pattern-copying-prototypes
title: Prototype copying and nested state
level: basic
minutes: 3
sourceLesson: pattern-creational
summary: A shallow copy retains references to nested objects.
---

## Prototype pattern

### The problem

Making an object from scratch is expensive or complicated, but you have a configured example. You want "another one like that", without knowing its concrete class.

### The structure

```
 Client ---> Prototype
             +clone() -> copy
                ^
                |
          ConcretePrototype
          clone(): copy self
```

### In Python

Python's `copy` module is the prototype pattern. `copy.copy()` makes a shallow copy; `copy.deepcopy()` recursively copies supported components, respecting memoisation and class hooks. It keeps objects that are shared within the copied structure shared in the copy, and returns some objects, including functions and classes, unchanged. Classes customise this with `__copy__` and `__deepcopy__`.

```python
import copy

base = {"retries": 3,
        "headers": {"User-Agent": "app"}}

# Only the outer dictionary is copied.
a = copy.copy(base)
a["headers"]["X-Trace"] = "1"
print("X-Trace" in base["headers"])
# True: shallow copy shares the dict

# Copy the nested headers as well.
b = copy.deepcopy(base)
b["headers"]["X-Id"] = "2"
print("X-Id" in base["headers"])
# False: deep copy has its own dict
```

### When not to use it

- When construction is cheap: just call the constructor.
- When objects hold resources that can't be meaningfully copied (open sockets, locks, open file objects). `deepcopy` cannot infer the right resource policy. It may raise an error; custom copy hooks may deliberately share or recreate a resource, and that policy needs explicit design.
- When the shallow/deep distinction will confuse readers. Shared nested state is a classic source of bugs.

### In real libraries

- **Python's `copy` module** and the `__copy__`/`__deepcopy__` hooks.
- **Java's `Object.clone()`** and the `Cloneable` interface (widely regarded as awkward; copy constructors are usually preferred).
- **JavaScript's prototypes** share the name and a similar spirit: objects inherit from another object rather than a class.

## Key takeaways
- A shallow copy retains references to nested objects.
- A deep copy recursively copies supported components and respects memoisation and class hooks.
- Resource-owning objects need an explicit lifecycle rather than blind copying.

## Further reading
- [copy — Python documentation](https://docs.python.org/3/library/copy.html)
