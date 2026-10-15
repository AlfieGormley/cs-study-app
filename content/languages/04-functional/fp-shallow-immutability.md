---
id: fp-shallow-immutability
title: Bindings, values and shallow immutability
level: basic
minutes: 3
sourceLesson: fp-pure-functions
summary: An immutable binding does not freeze the referenced value.
---

An immutable binding does not freeze the referenced value. This unit develops that mechanism using the earlier units as prerequisites.

## Immutability

A value is **immutable** if it cannot change after it is created. Immutability and purity reinforce each other: deeply immutable data cannot be mutated through those arguments. Sharing it between threads additionally needs safe publication and a lifetime that remains valid; immutable outer containers may still hold mutable contents.

Instead of changing a value, you create a new one that differs in the parts you care about:

```python
# Replacement leaves the first user intact.
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class User:
    name: str
    age: int

a = User("Ada", 36)
b = replace(a, age=37)   # new object
a.age = 40   # FrozenInstanceError
```

In JavaScript the idiom is spread syntax:

```javascript
// Copy own enumerable properties shallowly.
const a = { name: "Ada", age: 36 };
const b = { ...a, age: 37 };
// a is untouched
```

Ordinary Haskell records are immutable; record update constructs a new value. Explicit effectful facilities such as IORef and STRef also support mutable state:

```haskell
-- Record update creates a new User value.
data User = User { name :: String
                 , age  :: Int }

older :: User -> User
older u = u { age = age u + 1 }
```

## Bindings versus values

Two different things get called "immutable", and mixing them up causes bugs.

- **Immutable binding**: the *name* can't be pointed at something else. JavaScript `const`, Java `final`.
- **Immutable value**: the *object* can't be changed.

```javascript
// Changing contents differs from rebinding.
const xs = [1, 2, 3];
xs.push(4);     // allowed! xs is [1,2,3,4]
xs = [];        // TypeError: the binding
```

`const` freezes the arrow, not the box it points to.

## Shallow versus deep

Most language-level immutability is shallow: **shallow immutability** protects the outer object, not what it contains. **Deep immutability** would also protect everything inside it.

```python
# The tuple retains a mutable nested list.
t = (1, [2, 3])
t[1].append(4)
print(t)        # (1, [2, 3, 4])
hash(t)         # TypeError: unhashable
```

The tuple can't be changed, but the list inside it can. That tuple cannot be a dictionary key because lists are unhashable and tuple hashing requires hashable elements. Mutable user-defined objects can still be hashable by identity; mutability alone is not the hashability test.

JavaScript's `Object.freeze` is shallow in the same way:

```javascript
// Only the outer object is frozen.
const cfg = Object.freeze({
  db: { host: "a" }
});
cfg.port = 1;      // ignored (throws
                   // in strict mode)
cfg.db.host = "b"; // works: inner object
                   // is not frozen
```

For deep immutability use immutable types all the way down (tuples of tuples, `frozenset`, frozen dataclasses with frozen fields), or a library such as Immutable.js or Immer in JavaScript.

## Key takeaways
- An immutable binding does not freeze the referenced value.
- Shallow protection leaves nested mutable objects mutable.

## Further reading
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Python Model](https://docs.python.org/3/reference/datamodel.html)
- [Ecma Object](https://tc39.es/ecma262/multipage/fundamental-objects.html)
- [Haskell6](https://www.haskell.org/onlinereport/haskell2010/haskellch6.html)
