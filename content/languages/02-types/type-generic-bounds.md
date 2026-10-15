---
id: type-generic-bounds
title: Bounds and richer generic abstractions
level: intermediate
minutes: 3
sourceLesson: type-generics
summary: Bounds grant specific operations such as ordering or a length property.
---

Generic code can preserve an unknown type without knowing its operations. A bound makes the required capabilities explicit instead of assuming every value can be compared or inspected.

## Bounded generics

Fully parametric code can't *do* much with a `T`: it can store it, return it and pass it along, but not compare or print it. To use operations, you **bound** the type parameter: "any `T`, as long as it supports X".

```java
static <T extends Comparable<T>>
T max(List<T> xs) { ... }
```

```rust
fn largest<T: PartialOrd + Copy>(
    xs: &[T],
) -> T {
    // Requires at least one element.
    let mut best = xs[0];
    for &x in xs {
        // Keep a greater comparable value.
        if x > best { best = x; }
    }
    best
}
```

```haskell
maximum' :: Ord a => [a] -> a
```

```ts
function longest<
  T extends { length: number }
>(a: T, b: T): T {
  // Return an input, preserving its type.
  return a.length >= b.length ? a : b;
}
longest("abc", "de");  // ok
longest(10, 20);       // error: number
                       // has no 'length'
```

In Python, a bound can be a `Protocol`, which checks structurally:

```python
from typing import Protocol, Self

class Ordered(Protocol):
    def __lt__(self, other: Self) -> bool:
        ...

def biggest[T: Ordered](xs: list[T]) -> T:
    best = xs[0]
    # Compare the remaining values.
    for x in xs[1:]:
        if best < x:
            best = x
    return best
```

These maximum examples require nonempty inputs and meaningful ordering; `PartialOrd` also admits incomparable values such as NaN, so the Rust loop is not a universal mathematical maximum. mypy accepts `biggest([3, 9, 4])` (result `int`) and rejects `biggest([object()])`, because `object` has no usable `__lt__`.

## Beyond the basics

- **Generic types**, not just functions: `struct Pair<A, B>`, `Map<K, V>`, `Result<T, E>`.
- **Higher-kinded types** abstract over type constructors themselves. Haskell's `Functor f` works for any `f` such as `Maybe` or `[]`: `fmap :: (a -> b) -> f a -> f b`. Java, TypeScript and Rust do not expose that same direct Haskell-style type-constructor parameter; encodings and other abstractions are separate possibilities.
- **C++ templates** check non-dependent constructs at definition and dependent constructs during instantiation. C++20 concepts express constraints checked when a specialization is considered.

## Avoid a parameter without a relationship

- **Needless type parameters.** The TypeScript handbook's rule: if a type parameter appears only once, you probably don't need it. `function log<T>(x: T): void` is no better than `log(x: unknown)`.

## Key takeaways
- Bounds grant specific operations such as ordering or a length property.
- A partial ordering need not provide a mathematical maximum for incomparable values.
- Higher-kinded parameters abstract over constructors; templates have definition- and instantiation-time checks.

## Further reading
- [Rust standard library: PartialOrd](https://doc.rust-lang.org/std/cmp/trait.PartialOrd.html)
- [TypeScript Handbook: Functions](https://www.typescriptlang.org/docs/handbook/2/functions.html)
- [PEP 695: Type parameter syntax](https://peps.python.org/pep-0695/)
- [C++ draft: Template name resolution](https://eel.is/c++draft/temp.res)
- [Haskell 2010: Declarations and types](https://www.haskell.org/onlinereport/haskell2010/haskellch4.html)
