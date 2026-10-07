---
id: fp-pure-functions
title: Pure functions and immutability
level: basic
minutes: 9
summary: What makes a function pure, why referential transparency matters, and how immutability works (and leaks) in Python, JavaScript and Haskell.
---

Functional programming rests on one idea: build programs out of functions that behave like the functions in maths. Give `square` the number 3 and you get 9. Today, tomorrow, on any machine, however many times you ask.

Many functions in everyday code are not like that. They read a global, write to a database, print a log line or change the list you passed in. Functional programming does not ban those things (programs that do nothing observable are useless). It **pushes them to the edges**, so that the bulk of the code is made of pieces you can reason about on their own.

## What makes a function pure

A function is **pure** when both of these hold:

1. **Same inputs, same output.** The result depends only on the arguments. No dependence on clocks, random state, files or mutable globals that can change between calls; reading a fixed immutable constant is compatible with purity.
2. **No side effects.** Calling it changes nothing observable outside it: no mutation of arguments or globals, no I/O, no exceptions used as hidden control flow to the outside world.

```python
# Pure
def total(prices):
    return sum(prices)

# Impure: reads a global that can change
TAX = 0.2
def with_tax(price):
    return price * (1 + TAX)

# Impure: mutates its argument
def add_item(cart, item):
    cart.append(item)
    return cart

# Impure: depends on the clock
import time
def greeting():
    h = time.localtime().tm_hour
    return "Morning" if h < 12 else "Hi"
```

These Python examples assume ordinary built-in numeric values and finite containers, without effectful custom operators or concurrent mutation. Purity here concerns returned values rather than allocation identity; returning mutable objects needs care if callers share or mutate them.

Local mutation inside a function is fine. A function that builds a list with a loop and returns it is still pure, as long as nothing outside can see the mutation happen.

```python
def squares(n):
    out = []          # local, invisible
    for i in range(n):
        out.append(i * i)
    return out        # still pure
```

## Referential transparency

A pure function call is **referentially transparent**: you can replace the call with its result without changing what the program does. If `total([2, 3])` is pure, every occurrence of it can be swapped for `5`.

This is what makes pure code easy to reason about. You can read it like algebra:

```
y = f(x) + f(x)
z = f(x)
y = z + z          # reuse a pure result
```

If `f` printed something, or incremented a counter, the two lines would behave differently. That one rewrite is the basis of a whole list of practical benefits.

| Benefit | Why purity gives it |
|---|---|
| Testing | Dependencies supplied as inputs; no I/O mocks for the pure core |
| Caching | Same input means same output, so memoise |
| Parallelism | No shared state to race on |
| Refactoring | Calls can be moved, merged or removed |
| Debugging | Reproduce a bug with just the inputs |

Memoisation is the clearest example. `functools.lru_cache` preserves intended behavior when reusing a result is valid: arguments must be hashable, relevant inputs stable, and callers must not require a fresh mutable object. Explicitly managed caches can also tolerate documented staleness for impure I/O. Put it on `greeting()` and it would say "Morning" all day.

> [!note] Compilers love purity too
> GHC (the main Haskell compiler) can eliminate common subexpressions, inline and reuse pure expressions when doing so preserves semantics; divergence, exceptions and space usage still matter. C compilers can also optimize calls when analysis or annotations establish relevant properties.

## Functional core, imperative shell

Real programs must do I/O. The standard pattern, popularised by Gary Bernhardt, is a **functional core** wrapped in an **imperative shell**:

```
+------------------------------------+
| shell: read request, query DB,     |
|        call APIs, write response   |
|   +----------------------------+   |
|   | core: pure functions that  |   |
|   | decide what to do, given   |   |
|   | plain data                 |   |
|   +----------------------------+   |
+------------------------------------+
```

```python
# Core: pure, trivially testable
def apply_discount(order, today):
    if today.weekday() == 4:  # Friday
        t = order["total"] * 0.9
        return {**order, "total": t}
    return order

# Shell: impure, kept thin
def handle(order_id):
    order = db.load(order_id)
    today = date.today()
    new = apply_discount(order, today)
    db.save(new)
```

Notice the trick: instead of calling `date.today()` inside the core, the shell passes the date in. The impurity has been turned into a parameter. Tests can pass any date they like.

## Immutability

A value is **immutable** if it cannot change after it is created. Immutability and purity reinforce each other: if data can't change, a function can't mutate its arguments, and sharing data between functions or threads is safe.

Instead of changing a value, you create a new one that differs in the parts you care about:

```python
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
const a = { name: "Ada", age: 36 };
const b = { ...a, age: 37 };
// a is untouched
```

Ordinary Haskell records are immutable; record update constructs a new value. Explicit effectful facilities such as IORef and STRef also support mutable state:

```haskell
data User = User { name :: String
                 , age  :: Int }

older :: User -> User
older u = u { age = age u + 1 }
```

### Bindings versus values

Two different things get called "immutable", and mixing them up causes bugs.

- **Immutable binding**: the *name* can't be pointed at something else. JavaScript `const`, Java `final`.
- **Immutable value**: the *object* can't be changed.

```javascript
const xs = [1, 2, 3];
xs.push(4);     // allowed! xs is [1,2,3,4]
xs = [];        // TypeError: the binding
```

`const` freezes the arrow, not the box it points to.

### Shallow versus deep

Most language-level immutability is **shallow**. It protects the outer object, not what it contains.

```python
t = (1, [2, 3])
t[1].append(4)
print(t)        # (1, [2, 3, 4])
hash(t)         # TypeError: unhashable
```

The tuple can't be changed, but the list inside it can. That tuple cannot be a dictionary key because lists are unhashable and tuple hashing requires hashable elements. Mutable user-defined objects can still be hashable by identity; mutability alone is not the hashability test.

JavaScript's `Object.freeze` is shallow in the same way:

```javascript
const cfg = Object.freeze({
  db: { host: "a" }
});
cfg.port = 1;      // ignored (throws
                   // in strict mode)
cfg.db.host = "b"; // works: inner object
                   // is not frozen
```

For deep immutability use immutable types all the way down (tuples of tuples, `frozenset`, frozen dataclasses with frozen fields), or a library such as Immutable.js or Immer in JavaScript.

## The classic pitfalls

### Python's mutable default argument

Default values are evaluated **once**, when the `def` runs, not on each call:

```python
def add(item, bag=[]):
    bag.append(item)
    return bag

add(1)   # [1]
add(2)   # [1, 2]  same list!
```

Use `bag=None` and create a new list when it is None; this still mutates an explicitly supplied list. To avoid mutation altogether, use `def add(item, bag=()): return [*bag, item]`.

### In-place versus copying methods

Many standard library methods mutate. Know which:

| Mutates | Returns new |
|---|---|
| `list.sort()` | `sorted(list)` |
| `list.reverse()` | `list[::-1]` |
| JS `arr.sort()` | JS `arr.toSorted()` |
| JS `arr.reverse()` | JS `arr.toReversed()` |
| JS `arr.splice()` | JS `arr.toSpliced()` |

JavaScript added the `toSorted`, `toReversed`, `toSpliced` and `with` methods in ES2023 to provide copying counterparts to mutating operations.

### Aliasing

Two names, one object. A change through one is visible through the other.

```python
a = [1, 2]
b = a
b.append(3)
print(a)   # [1, 2, 3]
```

With immutable data, aliasing is harmless, which is why functional languages share structure freely (see the lesson on persistent data structures).

## Costs and trade-offs

Purity and immutability are not free.

- **Copying.** Naively copying a 1-million-element list to change one item is O(n). Persistent balanced trees and vector tries share unchanged parts and can give O(log n) updates; persistent linked-list indexed updates remain linear.
- **Garbage.** Creating new values constantly means more allocation. Modern generational garbage collectors handle short-lived objects cheaply, but it still matters in hot loops.
- **Awkward fits.** Some algorithms (in-place quicksort, union-find, graph algorithms over adjacency arrays) are naturally imperative. Haskell offers the `ST` monad for local mutation that stays invisible from outside.
- **Language support.** In Python and JavaScript immutability is a discipline, not a guarantee. Nothing stops a colleague mutating your "immutable" dict.

> [!tip] Where it pays off most
> React state hooks compare next and previous state using Object.is; React-Redux useSelector uses strict equality by default. Mutating and returning the same object can suppress the update-driven render; unrelated renders can still occur. Immutable updates make identity a useful change signal.

## Key takeaways
- A pure function's output depends only on its inputs, and calling it has no observable side effects.
- Referential transparency (replacing a call with its value) is what makes pure code testable, cacheable and safe to parallelise.
- Keep I/O in a thin imperative shell; pass impure inputs like the current time in as parameters.
- `const` and `final` make bindings immutable, not values. Tuples, frozen dataclasses and `Object.freeze` are shallow.
- Watch for mutable default arguments, mutating methods and aliasing.

## Further reading
- [Pure function — Wikipedia](https://en.wikipedia.org/wiki/Pure_function)
- [Referential transparency — Wikipedia](https://en.wikipedia.org/wiki/Referential_transparency)
- [Object.freeze() — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/freeze)
- [dataclasses (frozen instances) — Python docs](https://docs.python.org/3/library/dataclasses.html)
- [Functional Programming HOWTO — Python docs](https://docs.python.org/3/howto/functional.html)
- [Primary verification source 1](https://docs.python.org/3/library/functools.html)
- [Primary verification source 3](https://docs.python.org/3/reference/datamodel.html)
- [Primary verification source 4](https://tc39.es/ecma262/multipage/indexed-collections.html)
- [Primary verification source 5](https://react.dev/reference/react/useReducer)
- [Primary verification source 6](https://www.haskell.org/onlinereport/haskell2010/haskellch6.html)
